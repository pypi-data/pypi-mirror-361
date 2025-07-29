# Python Custom MessageBox using Customtkinter

## Description:

This Python package has a custom messagebox using Customtkinter and the Fredoka One font.

## What's included?

- Fredoka One font
- 5 custom messageboxes
- A messagebox with an OK button
- A messagebox with OK/Cancel buttons and a scroll bar
- A messagebox with Yes/No buttons
- A messagebox with Yes/No/Cancel buttons
- A messagebox with a textbox and OK/Cancel buttons

## Installation:

`
pip install tkcustomessagebox
`

After running pip, make sure your Fredoka One font it is in the current working directory, or download it from https://fonts.google.com/selection. <br> After downloading, extract the file and choose Fredoka-Bold.ttf 
Move Fredoka-Bold.ttf (Fredoka-Bold.ttf is the individual filename) only the file to the current working directory you host your project.

If you don't download the font, a `FontError` will occur.

## Messagebox sizing options (in `centermsgboxwin` function):

| Function Parameter Name | Definition |
|---|---|
| `win` = `CTkToplevel` | The master which is defaulted to `CTkToplevel`. |
| `width` = `int` | The width of the custom messagebox. (defaulted to 1000). |
| `height` = `int` | The height of the custom messagebox. (defaulted to 500). |

## Messagebox customization options (in function parameter):

| Function Parameter Name | Definition |
|---|---|
| `msgboxtitle` = `str` | The title of your messagebox. |
| `titlemsg` = `str` (included only in customMsgBoxWithScrBar function) | The title message inside of the messagebox above the scroll bar. |
| `textmsg` / `textmsgquestion` = `str` | The text message inside of your messagebox. |
| `bg_color` = `str` | The background color of your messagebox. |
| `btn_fg_color` = `str` | The background color of your buttons (inside). |
| `btn_text_color` = `str` | The text color inside your buttons. |
| `text_color` = `str` | The text color of `titlemsg` and `textmsg` / `textmsgquestion`. |
| `error` = `bool` (included only in `CustomMsgBox` function) | If `True`, a Windows error sound will play; if `False`, the default beep sound will play. |