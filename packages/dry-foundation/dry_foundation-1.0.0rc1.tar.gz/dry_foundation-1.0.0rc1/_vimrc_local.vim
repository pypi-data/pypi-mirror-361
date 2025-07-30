" Local Repository Settings
" ___________________________________________________
"
" (These settings are added by the `LucHermitte/local_vimrc` plugin)
"

if &filetype ==# "python"
  " Adjust PEP8 compliance for compatibility with black
  setlocal textwidth=88
  " Add columns to mark the end of long docstring lines and normal lines
  let &l:colorcolumn="73,".join(range(89,999),",")
endif
