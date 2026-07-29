" ============================================
" InCTF 2026 Finals — Vim Config
" TEAM_UNFINDABLES
" ============================================

" --- General ---
set nocompatible
syntax on
filetype plugin indent on
set encoding=utf-8
set number
set relativenumber
set cursorline
set showmatch
set wildmenu
set wildmode=longest:list,full
set laststatus=2
set ruler
set showcmd

" --- Search ---
set incsearch
set hlsearch
set ignorecase
set smartcase
" Clear search highlight with Escape
nnoremap <Esc> :nohlsearch<CR>

" --- Indentation ---
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab
set smartindent
set autoindent

" --- Performance ---
set lazyredraw
set ttyfast

" --- Split navigation ---
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" --- File handling ---
set autoread
set noswapfile
set nobackup
set undofile
set undodir=~/.vim/undodir

" --- Clipboard ---
set clipboard=unnamedplus

" --- Scrolling ---
set scrolloff=8
set sidescrolloff=8

" --- Status line ---
set statusline=
set statusline+=%#PmenuSel#
set statusline+=\ %f
set statusline+=\ %m
set statusline+=%=
set statusline+=\ %y
set statusline+=\ %l:%c
set statusline+=\ [%p%%]
set statusline+=\ 

" --- CTF Quick Templates ---
" \p = insert Python pwntools template
nnoremap <leader>p :read ~/.vim/templates/pwn.py<CR>
" \c = insert crypto template
nnoremap <leader>c :read ~/.vim/templates/crypto.py<CR>
" \w = insert web template
nnoremap <leader>w :read ~/.vim/templates/web.py<CR>

" --- Quick Run ---
" F5 = run current Python file
autocmd FileType python nnoremap <F5> :w<CR>:!python3 %<CR>
" F6 = run current bash script
autocmd FileType sh nnoremap <F5> :w<CR>:!bash %<CR>

" --- Color scheme ---
set background=dark
colorscheme desert

" Create undodir if it doesn't exist
silent !mkdir -p ~/.vim/undodir
