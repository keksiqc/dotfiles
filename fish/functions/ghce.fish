function ghce
    set -l __USAGE "Wrapper around `gh copilot explain` to explain a given input command in natural language.

    USAGE
        $argv[1] [flags] <command>

    FLAGS
        -d, --debug Enable debugging
        -h, --help  Display help usage

    EXAMPLES
        ... (Example descriptions remain as in the original)"
 
    for arg in $argv
        switch $arg
            case '-d' '--debug'
                set -gx GH_DEBUG api
            case '-h' '--help'
                echo $__USAGE
                return 0
        end
    end

    gh copilot explain $argv
end
