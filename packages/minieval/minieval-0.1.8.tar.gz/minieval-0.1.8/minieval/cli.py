import sys
from dataclasses import dataclass

from rich.console import Console
from rich.pretty import pprint

from minieval.launchers import init_writer
from minieval.backends import Backend, init_backend, init_template
from minieval.datatypes import Formatter, Instance, LMOutput, LMRequest, LauncherConfig, Metric, ModelConfig, Response, Scorer, TaskConfig, RequestType
from minieval.utils import apply_overrides

console = Console()

DEFAULT_SAVE_PATH = '/tmp/minieval'


@dataclass
class RunnerConfig:
    backend: Backend
    model: ModelConfig
    tasks: list[TaskConfig]
    launcher: LauncherConfig
    

class EvalRunner:
    def __init__(self, config: RunnerConfig):
        self.config = config

        self.llm = init_backend(
            backend_type=self.config.backend, 
            model_name=self.config.model.name
        )

        self.template_func = init_template(
            backend_type=self.config.backend,
            model_name=self.config.model.name
        )

        self.writer = init_writer(
            config = self.config.launcher
        )
    
    def run(self, task_config: TaskConfig):
        console.rule(f"[bold red]{task_config.alias}")

        from minieval.task_registry import TaskRegistry
        TaskClass = TaskRegistry.get_task(task_config.alias)
        
        task = TaskClass(config=task_config)
    
        instances: list[Instance] = task.requests
        few_shot_instaances: list[Instance] = task.build_few_shot()

        if task_config.limit:
            assert task_config.limit <= len(instances), \
                f'Limit is larger than the dataset! {task_config.limit=}, {len(instances)=}'
            instances = instances[:task_config.limit]

        formatter: Formatter = task_config.formatter
        scorers: list[Scorer] = task_config.scorer
        metrics: list[Metric] = task_config.metric

        messages: list[LMRequest] = formatter.build_messages(instances)

        requests: list[LMRequest] = formatter.build_requests(self.template_func, messages)

        if formatter.REQUEST_TYPE == RequestType.GENERATE:
            generations: list[LMOutput] \
                = self.llm.generate(requests, sampling_params=task_config.generation_kwargs)
        elif formatter.REQUEST_TYPE == RequestType.LOGPROBS:
            generations: list[LMOutput] \
                = self.llm.logprobs(requests, sampling_params=task_config.generation_kwargs)

        generations: list[LMOutput] \
            = task.extract_answers(generations)

        responses: list[Response] = []
        for inst, req, gen in zip(instances, requests, generations):
            responses += [Response(input=inst, request=req, output=gen)]

        pprint(responses[0], max_string=1000)

        for score in scorers:
            responses = score.score_responses(responses)
        
        for metric in metrics:
            responses = metric.compute_metrics(responses)

        pprint(responses[0], max_string=1000)

        dataset_metrics = self.reduce_metrics(responses)

        console.print(f"[dim]─── results ({task_config.alias}) ───[/dim]")
        
        pprint(dataset_metrics, expand_all=True)

        self.writer.save_responses(
            task_alias=task_config.alias, 
            responses=responses
        )
        
        self.writer.save_metrics(
            task_alias=task_config.alias, 
            metrics=dataset_metrics
        )

        return dataset_metrics

    def reduce_metrics(self, responses: list[Response]) -> dict:
        def average_dict(dicts: list[dict]) -> dict:
            """ Recursively average entries in a list of dicts """
            result = {}
            first = dicts[0]
            
            for key in first:
                if isinstance(first[key], dict):
                    values = [d[key] for d in dicts]
                    result[key] = average_dict(values)
                else:
                    values = [float(d[key]) for d in dicts]
                    result[key] = sum(values) / len(values)
                    
            return result
        
        all_scores = [response.scores for response in responses]
        
        return average_dict(all_scores)
    
    def evaluate(self):
        all_metrics = {}
        for task_config in self.config.tasks:
            all_metrics[task_config.alias] = self.run(task_config)
        return all_metrics


def run_eval(aliases, backend, model_name):
    from minieval.task_registry import TaskRegistry
    TaskRegistry() # initialize the registry

    # Init task config from registry
    tasks = []
    for alias in aliases:
        config: TaskConfig = TaskRegistry.get_config(alias)
        tasks.append(config)

    # Init model config
    model = ModelConfig(name=model_name)

    # Init save path
    launcher = LauncherConfig(save_path=DEFAULT_SAVE_PATH)

    config = RunnerConfig(
        backend = backend,
        model = model,
        tasks = tasks,
        launcher = launcher
    )

    config = apply_overrides(config)

    pprint(config, expand_all=True)

    runner = EvalRunner(config)

    all_metrics = runner.evaluate()

    console.print(f"[dim]─── all results ───[/dim]")

    pprint(all_metrics, expand_all=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="""minieval - A deviously simple eval library""")
    parser.add_argument('-t', '--tasks', nargs='+', help="Task aliases to evaluate")
    parser.add_argument('-m', '--model', default='mock', help="Model name/path to evaluate")
    parser.add_argument('-b', '--backend', default='mock', help="Backend to use (mock, vllm, litellm)")
    parser.add_argument('--list', action='store_true', help="List available tasks")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    # Allow unknown arguments to be passed as overrides
    args, unknown = parser.parse_known_args()
    
    if args.list:
        from minieval.task_registry import TaskRegistry
        pprint(TaskRegistry.names())
        return
        
    if not args.tasks:
        parser.error("the following arguments are required: -t/--tasks")
        
    # Override defaults with CLI args
    aliases = args.tasks
    backend = args.backend
    model_name = args.model
    
    run_eval(
        aliases,
        backend, 
        model_name,
    )


if __name__ == "__main__":
    main()
