# CheatTheSwitch

Desktop utility to split Nintendo Switch cheat files into per-cheat folders.

## Files
- `split_cheats_general.py`: your original reference script (unchanged)
- `cheat_splitter_core.py`: reusable split logic for app usage
- `cheat_splitter_app.py`: desktop GUI (file picker + optional drag/drop)

## Install
Python 3.10+ is recommended.

Optional (for drag/drop support):
```powershell
pip install tkinterdnd2
```

## Run GUI
```powershell
python cheat_splitter_app.py
```

## Output behavior
Default output:

`/path_to_cheat_file/game_name_or_id`

Rules:
- If path matches `.../{TID}/cheats/{BID}.txt`, then `game_name_or_id = TID`
- Otherwise `game_name_or_id = parent folder name`

If user selects a custom output folder:
- Option ON (default): app creates `<selected_output>/parent_folder_name/` first, then writes split cheats inside it.
- Option OFF: app writes split cheat folders directly under selected output.

When Option ON:
- `Use default parent folder name` ON: use auto name (`game_name_or_id`).
- `Use default parent folder name` OFF: user can type a custom parent folder name.

Unified output mode:
- Enable `Use unified output path for all files`.
- Select `Unified Output Path` once.
- Then split multiple files one by one without reselecting output each time.

Each cheat output file:

`<output>/<cheat_name>/cheats/<BID>.txt`
