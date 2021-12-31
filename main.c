#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

#define MAX_LINE 80 /* The maximum length command */

void run(char **args, char *input, int i);
int cut(char **args, char *input);
int check_sign(char **args, char *sign, int i);
int sign_pos(char **args, char *sign, int i);

int main(void) {
    char *args[MAX_LINE/2 + 1] = {NULL}; /* command line arguments */
    int should_run = 1; /* flag to determine when to exit program */
    char input[MAX_LINE];
    int previous_i = 0;

    while (should_run){
        int i=0;
        printf("mysh:~$ ");
        fflush(stdout);
        fgets(input,MAX_LINE,stdin);
        input[strlen(input)-1] = '\0';

        if(strcmp(input,"!!") == 0){
            if(args[0] == NULL){
                printf("No commands in history.\n");
            }
            else{
                i = previous_i;
            }
        }
        else if(strcmp(input, "exit") == 0){
            should_run = 0;
            break;
        }
        else{
            i = cut(args,input);
            previous_i = i;

        }

        if(should_run){
            run(args,input,i);
        }
        /** After reading user input, the steps are:
         * (1) fork a child process using fork()
         * (2) the child process will invoke execvp()
         * (3) parent will invoke wait() unless command included &
         */
    }

    return 0;
}

void run(char **args, char *input, int i){
    if(check_sign(args,"cd",i)){
        int n = sign_pos(args, "cd", i);
        if(chdir(args[n+1]) != 0){
            printf("cd: %s: No such file or directory\n", args[n+1]);
        }
    }
    else{
        pid_t pid = fork();
        if(pid<0){
            fprintf(stderr, "Fork Failed\n");
        }
        else if(pid == 0){
            if(check_sign(args,"&",i)){  // command with &
                int n = sign_pos(args, "&", i);
                args[n] = NULL;
                execvp(args[0], args);
                args[i-1] = "&";
            }
            else if(check_sign(args,">",i)){   // command with >
                int n = sign_pos(args, ">", i);
                FILE *file = fopen(args[n+1], "w");
                args[n] = NULL;
                dup2(fileno(file),STDOUT_FILENO);
                execvp(args[0],args);
                args[n] = ">";
                fclose(file);
            }
            else if(check_sign(args,"<",i)){
                int n = sign_pos(args, "<", i);
                FILE *file = fopen(args[n+1], "r");
                args[n] = NULL;
                dup2(fileno(file),STDIN_FILENO);
                execvp(args[0],args);
                args[n] = "<";
                fclose(file);
            }
            else if(check_sign(args,"|",i)){
                int n = sign_pos(args, "|", i);

                int fd[2];
                pipe(fd);
                char *args1[n+1], *args2[i-n];

                for(int x = 0;x<n;x++){
                    args1[x] = args[x];
                }
                args1[n] = NULL;

                for(int x = 0;x<i-n-1;x++){
                    args2[x] = args[x+n+1];
                }
                args2[i-n-1] = NULL;

                int pipe_pid = fork();

                if(pipe_pid > 0){
                    wait(NULL);
                    close(fd[1]);
                    dup2(fd[0],STDIN_FILENO);
                    execvp(args2[0],args2);
                    close(fd[0]);
                }
                else if(pipe_pid == 0){
                    close(fd[0]);
                    dup2(fd[1],STDOUT_FILENO);
                    execvp(args1[0],args1);
                    close(fd[1]);
                }
                else if(pipe_pid<0){
                    fprintf(stderr, "Fork Failed\n");
                }

                close(fd[0]);
                close(fd[1]);
            }
            else{
                execvp(args[0], args);
            }
        }
        else{
            if(strcmp(args[i-1],"&") != 0){
                while(wait(NULL) != pid);
            }
        }
    }
}

int cut(char **args, char *input){
    int i = 0;
    char *deep_twin = strdup(input);
    char *cut = strtok(deep_twin, " ");
    while(cut != NULL){
        args[i] = cut;
        i++;
        cut = strtok(NULL, " ");
    }
    args[i] = NULL;
    return i;
}

int check_sign(char **args, char *sign, int i){
    for(int n=0;n<i;n++){
        if(strcmp(args[n], sign) == 0){
            return 1;
        }
    }
    return 0;
}

int sign_pos(char **args, char *sign, int i){
    for(int n=0;n<i;n++){
        if(strcmp(args[n],sign)==0){
            return n;
        }
    }
}