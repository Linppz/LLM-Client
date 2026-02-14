from src.prompt_engine.template import PromptTemplate
from src.prompt_engine.schemas import RenderResult, FewShotExample


if __name__ == '__main__':
    example = FewShotExample(input = "hello", output = "perfect")
    example1 = FewShotExample(input = "helloe", output = "perfects")
    role = {"examples" : [example, example1], "lanuage":"python","your_code":"print(Hello world)", 'role':'猪',"constraints":['牢记你是大师','你需要非常尊重他人']}
    task = PromptTemplate("gpt-4o-mini","src/prompts")
    result = task.render(role, "code_review.j2")
    print(f'rendered_text:{result.rendered_text}\n, token_count:{result.token_count}\n, template_name:{result.template_name}\n, variable_used : {result.variables_used}')


    


