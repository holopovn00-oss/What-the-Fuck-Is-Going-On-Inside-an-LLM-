from pathlib import Path
import sys,re,json,shutil,subprocess
from content import S,C
R=Path('/workspace/scratch/54ca24749746'); O=R/'output/agents_chapter'; W=R/'tmp/agents_chapter'; O.mkdir(exist_ok=True)
F=O/'source/fonts';F.mkdir(parents=True,exist_ok=True)
for n in ['SourceSerif4-Regular.otf','SourceSerif4-Bold.otf','SourceSerif4-It.otf']:shutil.copy(R/'tmp/nature_selected'/n,F/n)
for n in ['HardingText.ttf','HardingText-Bold.ttf']:shutil.copy(R/'tmp/nature_exact'/n,F/n)
C.sort(key=lambda c:int(c['title'].split('.')[0]) if c['title'][0].isdigit() else 0)
C[0]['pages'][0]['side'] += r'\sidehead{Подтемы главы}' + '\n'.join(r'\hyperlink{topic'+str(i)+'}{'+c['title']+r'}\par' for i,c in enumerate(C) if i)
def esc(s):
 for a,b in [('&',r'\&'),('%',r'\%'),('#',r'\#'),('_',r'\_')]:s=s.replace(a,b)
 return s
head=r'''\documentclass[10pt,a4paper]{article}
\usepackage[left=17mm,right=16mm,top=14mm,bottom=17mm]{geometry}
\usepackage{fontspec,polyglossia}
\setdefaultlanguage{russian}
\setmainfont{SourceSerif4-Regular.otf}[Path=fonts/,BoldFont=SourceSerif4-Bold.otf,ItalicFont=SourceSerif4-It.otf]
\setsansfont{NimbusSans-Regular.otf}[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusSans-Bold.otf]
\newfontfamily\harding{HardingText.ttf}[Path=fonts/,BoldFont=HardingText-Bold.ttf]
\usepackage{unicode-math}\setmathfont{Latin Modern Math}
\usepackage{xcolor,amsmath,eso-pic,fancyhdr,needspace,changepage}
\definecolor{rulegray}{gray}{.5}
\usepackage[colorlinks=true,urlcolor=black,linkcolor=black,bookmarksnumbered=true]{hyperref}
\hypersetup{pdftitle={Архитектура агентов},pdfauthor={Атлас: исследовательская библиография},pdfsubject={Обзорная глава и локальная аннотированная библиография}}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{.3pt}
\fancyfoot[L]{\sffamily\fontsize{7.5}{9}\selectfont АТЛАС / АГЕНТЫ}\fancyfoot[R]{\sffamily\fontsize{8}{9}\selectfont\thepage}
\setlength{\footskip}{21pt}\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{1.5em}\widowpenalty=10000\clubpenalty=10000
\fancypagestyle{bibliopage}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}\fancyfoot[C]{\fontsize{10}{12}\selectfont\thepage}}
\fancypagestyle{articlepage}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{.3pt}\fancyfoot[L]{\sffamily\fontsize{7.5}{9}\selectfont АТЛАС / АГЕНТЫ}\fancyfoot[R]{\sffamily\fontsize{8}{9}\selectfont\thepage}}
\newif\ifbibpage
\newcommand{\thinrule}{\par{\color{rulegray}\hrule height .3pt}\par}
\newcommand{\subhead}[1]{\par\vspace{8pt}{\bfseries\fontsize{11}{13.2}\selectfont #1}\par\vspace{3pt}}
\newcommand{\sidehead}[1]{\par\vspace{10pt}\textbf{#1}\par\vspace{5pt}}
\newcommand{\step}[1]{\par\vspace{7pt}\textbf{#1}\par\vspace{3pt}}
\newsavebox{\maincolumn}\newsavebox{\sidecolumn}\newlength{\columnheight}\newlength{\columndepth}
\newcommand{\columns}[2]{
\begin{lrbox}{\maincolumn}\begin{minipage}[t]{.685\linewidth}\vspace{0pt}\fontsize{10.5}{13.4}\selectfont\setlength{\abovedisplayskip}{7pt}\setlength{\belowdisplayskip}{7pt}#1\end{minipage}\end{lrbox}
\begin{lrbox}{\sidecolumn}\begin{minipage}[t]{.266\linewidth}\vspace{0pt}\raggedright\sffamily\fontsize{9}{11.6}\selectfont#2\end{minipage}\end{lrbox}
\setlength{\columndepth}{\dp\maincolumn}\ifdim\dp\sidecolumn>\columndepth\setlength{\columndepth}{\dp\sidecolumn}\fi
\setlength{\columnheight}{\dimexpr\ht\maincolumn+\columndepth\relax}
\noindent\usebox{\maincolumn}\hfill\raisebox{-\columndepth}{\color{rulegray}\rule{.4pt}{\columnheight}}\hfill\usebox{\sidecolumn}}
\AddToShipoutPictureBG{\ifbibpage\else\AtPageLowerLeft{\color{rulegray}\put(41,42){\rule{.3pt}{760pt}}}\fi}
\begin{document}
'''
parts=[head]; md=['# Архитектура агентов\n\nАтлас · обзорная глава и адресная библиография · 12 сентября 2026\n\nСемь подтем. Числовые примеры учебные. Контроллеры, память, инструменты, инфраструктура, координация, длительная разработка и оценка.\n']
manifest=[]
def display_author(k):
 a=S[k]['author']
 if k in ['mcp','activity','workflow','eval']:return a
 tail=' и др.' if a.endswith(' et al.') else ''
 a=a.removesuffix(' et al.')
 names=[]
 for name in a.split(', '):
  t=name.split()
  names.append(t[-1]+', '+ ' '.join(w[0]+'.' for w in t[:-1]))
 return ', '.join(names)+tail

def category(k,i):
 return 'Вводные работы' if i==0 else S[k]['level']
group_order=['Вводные работы','Специализированные работы','Фронтир исследований']
for i,c in enumerate(C):
 c['refs']=sorted(c['refs'],key=lambda k:group_order.index(category(k,i)))
block_name='VI. Продвинутое профессиональное использование и агенты'
def running_header(i,j=0,bib=False):
 left=block_name if i==0 else 'Архитектура агентов'
 right='' if i==0 else C[i]['title'].split('. ',1)[1]
 return r'{\sffamily\fontsize{7.5}{9.5}\selectfont '+left+r'\hfill '+right+r'\par}\vspace{5pt}\thinrule\vspace{8pt}'

def textext(s,refs):
 def f(m):
  k,t=m.groups();assert k in refs,(k,refs);return r'\href{'+S[k]['url']+'}{'+t+r'\textsuperscript{'+str(refs.index(k)+1)+'}}'
 return re.sub(r'\\work\{([^{}]+)\}\{([^{}]+)\}',f,s)
def markdown(s):
 s=re.sub(r'\\work\{([^{}]+)\}\{([^{}]+)\}',lambda m:'['+m[2]+']('+S[m[1]]['url']+')',s)
 s=re.sub(r'\\href\{([^{}]+)\}\{\\textbf\{([^{}]+)\}\}',r'[\2](\1)',s)
 s=re.sub(r'\\(subhead|sidehead)\{([^{}]+)\}',r'\n### \2\n',s)
 s=re.sub(r'\\hyperlink\{topic([0-9]+)\}\{([^{}]+)\}',r'\2',s)
 s=re.sub(r'\\step\{([^{}]+)\}',r'\n**\1**\n\n',s).replace(r'\par','\n\n')
 s=s.replace(r'\[','$$').replace(r'\]','$$').replace(r'\(','$').replace(r'\)','$')
 return s.strip()
for i,c in enumerate(C):
 refs=c['refs'];title=c['title']; manifest.append(dict(section=i,title=title,sources=refs))
 for j,p in enumerate(c['pages']):
  if i or j:parts.append(r'\clearpage')
  if j==0:parts.append(r'\hypertarget{topic'+str(i)+r'}{}\pdfbookmark[0]{'+title+'}{section'+str(i)+'}')
  parts.append(running_header(i,j))
  if j==0:
   parts.append(r'{\fontsize{'+('25}{28' if i==0 else '21}{24')+r'}\selectfont '+(r'Архитектура агентов' if i==0 else title)+r'\par}\vspace{8pt}')
   parts.append(r'{\fontsize{11.5}{14.5}\selectfont '+c['lead']+r'\par}\vspace{7pt}\thinrule')
  parts.append(r'\columns{'+textext(p['main'],refs)+'}{'+textext(p['side'],refs)+'}')
  if j==0:md+=['\n## '+title+'\n\n'+c['lead']+'\n']
  md+=['\n'+markdown(p['main'])+'\n\n'+markdown(p['side'])+'\n']
 parts.append(r'\clearpage\pdfbookmark[1]{Библиография: '+title+'}{bib'+str(i)+'}')
 parts.append(r'\bibpagetrue\pagestyle{bibliopage}\begingroup\setlength{\parskip}{0pt}\setlength{\emergencystretch}{3em}\begin{adjustwidth}{3mm}{3mm}\vspace*{0pt}')
 parts.append(r'{\centering\fontsize{14}{18}\selectfont\addfontfeatures{LetterSpace=3}БИБЛИОГРАФИЯ\par}\vspace{8pt}{\centering\rule{.72\linewidth}{.35pt}\par}\vspace{6pt}')
 md+=['\n### Библиография\n']
 previous_group=None
 for n,k in enumerate(refs,1):
  s=S[k]
  level=category(k,i)
  if level!=previous_group:
   parts.append(r'\Needspace{180pt}\vspace{6pt}{\centering\fontsize{9.5}{12}\selectfont\addfontfeatures{LetterSpace=4}'+level.upper()+r'\par}\vspace{6pt}')
   md+=['\n#### '+level+'\n']
   previous_group=level
  author=display_author(k)
  original=str(n)+r'.\enspace '+esc(author)+' ('+esc(s['year'])+r'), \href{'+s['url']+r'}{\textit{'+esc(s['title'])+'}}. '+esc(s['kind'])+'.'
  where=esc(s['where']).replace('примеры связей',r'\newline примеры связей')
  parts.append(r'\begin{minipage}[t]{\linewidth}\vspace{0pt}\fontsize{10.5}{12.8}\selectfont{\hangindent=1.4em\hangafter=1 '+original+r'\par}\vspace{4pt}{\leftskip=1.4em '+esc(s['ru'])+r'\par\vspace{6pt}'+esc(s['note'])+r'\par\vspace{5pt}\textit{Что читать.} '+where+r'\par}\end{minipage}\par\vspace{6pt}')
  md+=['\n'+str(n)+'. '+author+' ('+s['year']+'), *['+s['title']+']('+s['url']+')*. '+s['kind']+'.\n\n'+s['ru']+'\n\n'+s['note']+'\n\n*Что читать.* '+s['where']+'\n']
 parts.append(r'\vspace{6pt}{\fontsize{10}{12.8}\selectfont\textit{Порядок чтения.} '+c['route']+r'\par}\end{adjustwidth}\endgroup\clearpage\bibpagefalse\pagestyle{articlepage}')
 md+=['\n**Порядок чтения.** '+c['route']+'\n']
parts.append(r'\end{document}')
tex='\n'.join(parts)
(O/'source/chapter.tex').write_text(tex)
sys.path.insert(0,str(R/'tmp/nature_selected/vendor'));import pyphen
h=pyphen.Pyphen(lang='ru_RU');a,b=tex.split(r'\begin{document}',1)
b=re.sub(r'[А-Яа-яЁё]{6,}',lambda m:h.inserted(m[0],hyphen=r'\-'),b)
(O/'source/typeset.tex').write_text(a+r'\begin{document}'+b)
(O/'agents_chapter.md').write_text('\n'.join(md))
(O/'source/sources.json').write_text(json.dumps(dict(checked='2026-09-12',sources={k:dict(v,included_in_pdf=any(k in c['refs'] for c in C),access=S[k]['access']) for k,v in S.items()},sections=manifest),ensure_ascii=False,indent=2))
for run in range(2):
 z=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','typeset.tex'],cwd=O/'source',capture_output=True,text=True)
 (W/'compile_output.txt').write_text(z.stdout)
 if z.returncode:print(z.stdout[-4200:]);raise SystemExit(z.returncode)
shutil.copy(O/'source/typeset.pdf',O/'atlas_agents_architecture.pdf')
print('Created',O/'atlas_agents_architecture.pdf','sections',len(C),'sources',len(S))
print('\n'.join(l for l in z.stdout.splitlines() if any(k in l for k in ['Overfull','Missing character','Output written'])))
