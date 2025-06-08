function ghcs
    # Set default target to 'shell'
    set -l TARGET "shell"

    # Read usage information into a variable
    set -l __USAGE "Wrapper around `gh copilot suggest` to suggest a command based on a natural language description of the desired output effort.
    Supports executing suggested commands if applicable.

    USAGE
        $argv[1] [flags] <prompt>

    FLAGS
        -d, --debug         Enable debugging
        -h, --help          Display help usage
        -t, --target target Target for suggestion; must be shell, gh, git
                            default: $TARGET

    EXAMPLES
        ... (Example descriptions remain as in the original)"

    for arg in $argv
        switch $arg
            case '-d' '--debug'
                set -gx GH_DEBUG api
            case '-h' '--help'
                echo $__USAGE
                return 0
            case '-t' '--target'
                if test (count $argv) -ge 2
                    set -l TARGET $argv[2]
                    set argv (seq 3 (count $argv))
                else
                    echo 'Error: Missing target argument after -t/--target'
                    return 1
                end
        end
    end

    set -l TMPFILE (mktemp -t gh-copilotXXX)
    function cleanup 
        rm -f $TMPFILE
    end

    gh copilot suggest -t $TARGET $argv --shell-out $TMPFILE

    # Execute the command if possible
    if test -s $TMPFILE
        set -l FIXED_CMD (cat $TMPFILE)
        # Add to command history without saving immediately
        history --add (history --query | head -n 1 | cut -d ' ' -f4-) $FIXED_CMD
        echo
        eval $FIXED_CMD
    else
        return 1
    end
end
