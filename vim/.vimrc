"
" 涛哥的vim配置文件
" huangtao117@gmail.com
"

" 设定默认编码 
set fenc=utf-8
set fencs=utf-8,usc-bom,gbk,gb18030,gb2312,cp936

" 语法高亮
syntax on

" 自动缩进
" 非c/c++推荐使用smartindent并注释下面2行
" set smartindent
set autoindent
set cindent

" TAB展开为空格
set expandtab

" 自动缩进的空白长度
set shiftwidth=4

" 制表符(4个空格)
set tabstop=4
set softtabstop=4

" 显示行号
set nu

" 修改注释颜色
highlight Comment ctermfg=DarkCyan guifg=DrakCyan
