# vim-ai provider OpenAI Reponse API

[vim-ai](https://github.com/madox2/vim-ai) provider plugin for OpenAI's Response API.

## Installation

1. Ensure `madox2/vim-ai` is installed.
1. Add `kevincojean/vim-ai-provider-openai-responses` to your Vim plugin manager.
    > ```vim
    >  Plug 'madox2/vim-ai'
    >  Plug 'kevincojean/vim-ai-provider-openai-responses'
    >  ```
1. The plugin will automatically install the `openai` python plugin after installation.
   > You may disable this behaviour by setting `g:vim_ai_openai_responses_enable_autoinstall = 0` in your `vimrc`. Then you may call the `VimAiOpenAiResponsesInstallDependencies` command to install the dependency manually.

### API key

Set your OpenAI API Key either by:  
**exporting**
```sh
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

**or using `token_file_path` as an option in your configuration**:

```ini
options.token_file_path = ~/.config/openai.token
```

## Configuration

You can configure a custom role or use vim-ai's configuration variable for the OpenAI Responses API `g:vim_ai_openai_responses_config`.

The list of options you may pass are numerous and documented by OpenAI:  
[https://platform.openai.com/docs/api-reference/responses](https://platform.openai.com/docs/api-reference/responses)

The following flags may be set in your `vimrc` to influence specific behaviours.  
- `g:vim_ai_openai_responses_enable_autoinstall`: `1` to enable auto-install at start, this is slow.
- `g:vim_ai_openai_responses_config`: overridable configuration for the openai responses api.

### VimAI configuration example

```vim
let g:vim_ai_openai_responses_config = {
\  "model": "gpt-4o-mini",
\  "endpoint_url": "https://api.openai.com/v1/responses",
\  "stream": "True",
\  "token_file_path": "~/.config/openai.token",
\ }
```

### Role configuration example

Making an assistant for generating text UML diagrams.  
It is connected to a vector store which has a 600 page pdf documentation of the `plantuml` syntax.
You force the assistant to use the vector store with the `options.tools.type = file_search` option.

```ini
[umldiagram.assistant]
provider = openai_responses
options.model = gpt-4.1
options.stream = true
options.tools.type = file_search
options.tools.vector_store_ids = [your_vector_store_uid]
options.store = false
prompt =
    You help me write UML diagrams in Vim.
    Your answers should be enclosed in the following block of markdown syntax:
    ```plantuml
    @startuml
    [your answers go here]
    @enduml
    ```
    Before giving me a diagram, you follow the following steps:
    1. You proactively identify parts of the diagram which need clarification and you ask me those questions sequentially.
    2. You suggest the best kind of PlantUML compatible diagram for the use case.
    3. You generate a diagram. You use the markdown ```plantuml``` syntax.
    4. Iterate until the user is completely satisfied.
```

## License

[MIT License](https://github.com/madox2/vim-ai-google-provider/blob/main/LICENSE)
