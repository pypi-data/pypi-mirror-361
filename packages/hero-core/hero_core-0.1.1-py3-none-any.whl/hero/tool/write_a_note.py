from typing import Dict
import traceback
from hero.util import log, function, stream

class WriteANote:
    def __init__(self):
        self.name = "write_a_note"
        self.prompt = """
<tool name="write_a_note">
    <desc>Record the key assumptions, thoughts, experiments, reflections, improvements, analysis, information, key details or draw up a plan into a file (append mode, not overwrite) and `task_execute_history` for later reference during subsequent tasks.</desc>
    <params>
        <note type="string">The key assumptions, thoughts, experiments, reflections, improvements, analysis, information, key details or draw up a plan.</note>
        <write_file type="string">The name of the file to append the note to.</write_file>
    </params>
    <example>
        {
            "tool": "write_a_note",
            "params": {
                "note": "The key information.", "write_file": "note.md"
            }
        }
    </example>
</tool>
"""

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt


    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ) -> Dict[str, str]:
        try:
            note = params.get("note")
            write_file = params.get("write_file")

            if not note:
                raise ValueError("Missing required parameter: note")
            if not write_file:
                raise ValueError("Missing required parameter: write_file")

            log.debug(f"write_a_note: {note}")
            log.debug(f"write_a_note: {write_file}")

            note = f"<note>\n{note}\n</note>\n\n"

            function.append_file(caller.get("dir"), write_file, note)

            stream.push(
                component="editor",
                action="open_file",
                timestamp=function.timestamp(),
                payload={
                    "path": write_file,
                    "content": note
                }
            )

            return {
                "status": "success",
                "message": f"Note appended to {write_file}",
            }

        except Exception as e:
            log.error(f"write_a_note error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }