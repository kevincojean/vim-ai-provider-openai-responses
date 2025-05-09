let g:my_requirements_file = 'requirements.txt'

function! GetPipCommand()
    " Get the proper system-specific pip or pip3 command for installation of required packages.
    let pip_command = system('python -m pip --version')
    if v:shell_error
        let pip_command = system('python3 -m pip --version')
        if v:shell_error
            echom "pip is not installed. Please install pip first."
            return ''
        endif
        return 'python3 -m pip'
    endif
    return 'python -m pip'
endfunction

function! VimAiOpenAiResponsesInstallDependencies()
    let pip_command = GetPipCommand()
    if pip_command == ''
        return
    endif
    if !filereadable(g:my_requirements_file)
        echom "Requirements file not found: " . g:my_requirements_file
        return
    endif
    let command = pip_command . ' install -r ' . g:my_requirements_file
    let result = system(command)
    if v:shell_error
        echom "Failed to install packages from requirements.txt"
        echom result
    else
        echom "Successfully installed packages from requirements.txt"
    endif
endfunction

" Command to manually install packages from requirements.txt if needed
command! VimAiOpenAiResponsesInstallDependencies call VimAiOpenAiResponsesInstallDependencies()

if !exists('g:vim_ai_openai_responses_enable_autoinstall')
    let g:vim_ai_openai_responses_enable_autoinstall = 1
endif
if g:vim_ai_openai_responses_enable_autoinstall == 1
    " Automatically install the required packages from requirements.txt when the plugin is loaded
    let result = system(GetPipCommand() . ' show openai')
    if v:shell_error != 0
        call VimAiOpenAiResponsesInstallDependencies()
    endif
endif

let g:vim_ai_openai_responses_config = {
\  "model": "gpt-4o-mini",
\  "endpoint_url": "https://api.openai.com/v1/responses",
\  "stream": "True",
\  "token_file_path": "~/.config/openai.token",
\ }

let s:plugin_root = expand('<sfile>:p:h:h')

call vim_ai_provider#Register('openai_responses', {
\  'script_path': s:plugin_root . '/py/openai_responses.py',
\  'class_name': 'OpenAiResponsesProvider',
\})
