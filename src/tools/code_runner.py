import logging
from typing import List, Optional

from llm_sandbox import SandboxSession

logger = logging.getLogger("code_runner")


def run_code(lang: str, code: str, libraries: Optional[List] = None) -> str:
    """
        Run code in a sandboxed environment.
        :param lang: The language of the code.
        :param code: The code to run.
        :param libraries: The libraries to use, it is optional.
        :return: The output of the code.
        """
    logger.info(f"Running {lang} code:")
    for line in code.split('\n'):
        if line:
            logger.info(f"\t{line}")

    with SandboxSession(lang=lang, verbose=True) as session:  # type: ignore[attr-defined]
        return session.run(code, libraries).text
