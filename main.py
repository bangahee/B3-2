from __future__ import annotations

# shlex는 CLI 형식의 문자열을 안전하게 분리하기 위해 사용한다.
#
# 일반 split()을 사용하면 다음 입력이 여러 조각으로 나뉜다.
#
# COMMIT "Add login feature"
#
# 하지만 shlex.split()을 사용하면 따옴표 안의 문자열을
# 하나의 인자로 처리할 수 있다.
import shlex

# Mini Git 저장소 상태와 명령어 기능을 관리하는 클래스를 가져온다.
from mini_git import MiniGit


def execute_command(
    repository: MiniGit,
    command: str,
    args: list[str],
) -> str:
    """
    입력된 명령어와 인자를 검증하고,
    해당하는 MiniGit 메서드를 호출한다.

    Args:
        repository:
            현재 실행 중인 MiniGit 저장소 객체이다.

            이 객체 안에 커밋, 브랜치, 현재 사용자,
            역색인 등의 상태가 저장되어 있다.

        command:
            사용자가 입력한 명령어이다.

            main()에서 소문자로 변환되기 때문에
            INIT, Init, init은 모두 "init"으로 전달된다.

        args:
            명령어 뒤에 입력된 인자 목록이다.

            예:
            COMMIT "Add login feature"

            command:
            "commit"

            args:
            ["Add login feature"]

    Returns:
        명령 실행 결과 또는 에러 메시지를 문자열로 반환한다.
    """

    # INIT 명령을 처리한다.
    #
    # 형식:
    # INIT <user_name>
    #
    # 사용자 이름은 정확히 하나의 인자여야 한다.
    if command == "init":
        if len(args) != 1:
            return "Invalid args"

        return repository.init_repository(args[0])

    # BRANCH 명령을 처리한다.
    #
    # 형식:
    # BRANCH <branch_name>
    #
    # 현재 HEAD를 가리키는 새 브랜치를 생성한다.
    if command == "branch":
        if len(args) != 1:
            return "Invalid args"

        return repository.create_branch(args[0])

    # SWITCH 명령을 처리한다.
    #
    # 형식:
    # SWITCH <branch_name>
    #
    # 존재하는 브랜치로 현재 브랜치를 변경한다.
    if command == "switch":
        if len(args) != 1:
            return "Invalid args"

        return repository.switch_branch(args[0])

    # COMMIT 명령을 처리한다.
    #
    # 형식:
    # COMMIT <message>
    #
    # 공백이 포함된 메시지는 따옴표로 감싸야
    # shlex.split() 결과에서 하나의 인자로 처리된다.
    if command == "commit":
        if len(args) != 1:
            return "Invalid args"

        return repository.create_commit(args[0])

    # LOG 명령을 처리한다.
    #
    # 지원 형식:
    # LOG
    # LOG --sort-by=date
    # LOG --sort-by=author
    if command == "log":
        # 인자가 없으면 부모 커밋 우선 순서로 로그를 출력한다.
        if len(args) == 0:
            return repository.show_log()

        # 정렬 옵션은 정확히 하나만 허용한다.
        if len(args) == 1:
            option = args[0]

            # 옵션도 대소문자를 구분하지 않도록 소문자로 변환한다.
            lower_option = option.lower()

            # 옵션이 --sort-by= 형식인지 확인한다.
            if lower_option.startswith("--sort-by="):
                # "=" 뒤의 정렬 기준만 분리한다.
                #
                # 예:
                # "--sort-by=date"
                #
                # 결과:
                # "date"
                sort_by = option.split("=", 1)[1].lower()

                return repository.show_sorted_log(sort_by)

        # 허용되지 않은 정렬 옵션이나 인자 개수이면 에러를 반환한다.
        return "Invalid args"

    # PATH 명령을 처리한다.
    #
    # 형식:
    # PATH <commit1> <commit2>
    #
    # 두 커밋 hash가 필요하므로 인자는 정확히 2개여야 한다.
    if command == "path":
        if len(args) != 2:
            return "Invalid args"

        return repository.show_path(
            start_hash=args[0],
            end_hash=args[1],
        )

    # ANCESTORS 명령을 처리한다.
    #
    # 형식:
    # ANCESTORS <commit_hash>
    #
    # 특정 커밋에서 부모 방향으로 도달 가능한
    # 모든 조상 커밋을 출력한다.
    if command == "ancestors":
        if len(args) != 1:
            return "Invalid args"

        return repository.show_ancestors(args[0])

    # SEARCH 명령을 처리한다.
    #
    # 지원 형식:
    # SEARCH <keyword>
    # SEARCH --author=<name>
    if command == "search":
        if len(args) != 1:
            return "Invalid args"

        # 검색 인자 원본을 저장한다.
        search_argument = args[0]

        # 옵션 비교는 대소문자를 구분하지 않도록
        # 소문자 형태도 함께 만든다.
        lower_argument = search_argument.lower()

        # --author= 옵션으로 시작하면 작성자 검색으로 처리한다.
        if lower_argument.startswith("--author="):
            # "=" 뒤의 작성자 이름만 분리한다.
            #
            # 예:
            # "--author=Alice"
            #
            # 결과:
            # "Alice"
            author = search_argument.split("=", 1)[1]

            return repository.search_author(author)

        # author 옵션이 아니면 일반 키워드 검색으로 처리한다.
        return repository.search_keyword(search_argument)

    # 위 조건에 해당하지 않는 명령어는 지원하지 않는 명령어이다.
    return f"Unknown command: {command}"


def main() -> None:
    """
    사용자가 exit 또는 quit을 입력할 때까지
    Mini Git REPL을 반복 실행한다.

    REPL은 다음 과정을 반복한다.

    Read:
        사용자 명령어를 입력받는다.

    Evaluate:
        입력을 파싱하고 해당 명령을 실행한다.

    Print:
        실행 결과를 출력한다.

    Loop:
        다음 명령어를 다시 입력받는다.
    """

    # MiniGit 객체를 반복문 밖에서 한 번만 생성한다.
    #
    # 이 객체가 프로그램 실행 중의 모든 상태를 저장한다.
    #
    # 만약 while문 안에서 매번 새로 생성하면
    # 명령을 입력할 때마다 커밋과 브랜치 정보가 초기화된다.
    repository = MiniGit()

    # 프로그램 시작 안내 문구를 출력한다.
    print("Mini Git")
    print("Enter 'exit' or 'quit' to close the program.")

    # 사용자가 종료 명령을 입력할 때까지 반복한다.
    while True:
        try:
            # mini-git> 프롬프트를 출력하고 사용자 입력을 받는다.
            #
            # strip()을 사용하여 문자열 앞뒤의 불필요한 공백을 제거한다.
            raw_command = input("mini-git> ").strip()

        # 입력 리다이렉션으로 테스트 파일을 실행한 뒤
        # 파일의 끝에 도달하면 EOFError가 발생할 수 있다.
        except EOFError:
            # 출력 줄을 정리한 뒤 프로그램을 종료한다.
            print()
            break

        # 사용자가 Ctrl+C를 입력한 경우 프로그램이 즉시 종료되지 않도록 한다.
        except KeyboardInterrupt:
            print("\nUse exit or quit to close Mini Git.")

            # 다시 다음 명령어를 입력받는다.
            continue

        # 빈 문자열이 입력되면 아무 작업도 하지 않고
        # 다음 명령 입력으로 넘어간다.
        if not raw_command:
            continue

        try:
            # 따옴표로 묶인 문자열을 하나의 인자로 처리한다.
            #
            # 입력:
            # COMMIT "Add login feature"
            #
            # 결과:
            # ["COMMIT", "Add login feature"]
            parts = shlex.split(raw_command)

        # 따옴표가 닫히지 않은 경우 shlex.split()이
        # ValueError를 발생시킬 수 있다.
        except ValueError:
            print("Invalid args")
            continue

        # 파싱 결과가 비어 있으면 다음 입력으로 넘어간다.
        if not parts:
            continue

        # 첫 번째 요소는 명령어이다.
        #
        # lower()를 적용하여 명령어가 대소문자를 구분하지 않도록 한다.
        command = parts[0].lower()

        # 첫 번째 요소 뒤의 값들은 명령어 인자이다.
        args = parts[1:]

        # exit 또는 quit을 입력하면 프로그램을 종료한다.
        if command in ("exit", "quit"):
            print("Mini Git closed.")
            break

        # 명령어 실행을 execute_command()에 위임한다.
        #
        # main()은 사용자 입력과 출력에 집중하고,
        # execute_command()는 명령어 검증과 기능 분기를 담당한다.
        result = execute_command(
            repository=repository,
            command=command,
            args=args,
        )

        # MiniGit 메서드에서 반환된 결과 문자열을 출력한다.
        print(result)


# 이 파일을 직접 실행했을 때만 main()을 호출한다.
#
# 예:
# python main.py
#
# 다른 파일에서 main.py를 import한 경우에는
# main()이 자동으로 실행되지 않는다.
if __name__ == "__main__":
    main()