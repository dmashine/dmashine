#!/usr/bin/env python
# -*- coding: utf-8-*-
# Скрипт автоматически проверяет статьи Инкубатора на обычные ошибки.
# Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
# Идея: Samal, участники Инкубатора
# Лицензирование: Общественное достояние / Beerware. Допускается любое
#   распространение и использование, а если меня встретите - налейте пива!


import re, wikipedia, catlib

class inc_helper:
  def __init__(self, page):
    self.page=page
    self.recense = ""
  def run(self):
    """Формирует на СО статьи комментарий"""
    pagetext=self.page.get()
    for i in [1,2,3]:
      pagetext=re.sub(r"{{[^{}]*}}", "***", pagetext, 0, re.DOTALL+ re.M) # Эти 2 некрасивые строки выпиливают из текста шаблоны, учитывая вложенность.

    wikipedia.output(pagetext, toStdout = True)
    pattern=re.compile("^ +\w*", re.M) #Начало строки-пробелы-любой печатаемый символ
    if pattern.search(pagetext) != None:
      self.recense += u"* Строки не должны начинаться с пробела, это портит оформление статей. Почитайте [[Википедия:Шпаргалка|шпаргалку по оформлению статей]].\r\n"
    pattern=re.compile("<.*br.*>") # Тэг br в тексте статьи
    if pattern.search(pagetext) != None:
      self.recense += u"* Для создания нового абзаца в Википедии принято использовать двойной перевод строки, а не тег <nowiki><br></nowiki>. В статьях Википедии тег <nowiki><br></nowiki> применяется только в очень редких специальных случаях.  Пожалуйста, посмотрите [[Википедия:Шпаргалка|краткое пособие по оформлению статей]].\r\n"
    pattern=re.compile("[( - )\"]") # короткий дефис с пробелами вокруг или не те кавычки
    if pattern.search(pagetext) != None:
      self.recense += u"* Хорошо бы пройтись [[Википедия:Проект:Инкубатор/Справочники и пособия/Викификатор|Викификатором]]. Желательно его использовать если не после каждой правки, то хотя бы эпизодически.\r\n"
    pattern=re.compile("\n") # Текст, потом один перевод строки, а за ним нет второго, или звёздочки или двоеточия(оформление списка)
    if pattern.search(pagetext) != None:
      self.recense += u"* Найдены абзацы, разделённые одиночным переводом строки. Если хотите начать новый абзац, ставьте перенос строки '''дважды'''. Основные приёмы викификации изложены в [[Википедия:Шпаргалка|Шпаргалке]].\r\n"
    pattern=re.compile(u"\[\[\:Категория\:.+?\]\]", re.M) # В статье должны быть категории
    if pattern.search(pagetext) == None:
      self.recense += u"* В статье не указаны категории. Пожалуйста, посмотрите [[Википедия:Проект:Инкубатор/Справочники и пособия/Как искать Категории|пособие по категоризации]].\r\n"

    #print u"%s"%self.page.titleWithoutNamespace
    #p=self.page.toggleTalkPage() # на СО
    p=wikipedia.Page(site, u"Участник:Drakosh/Лог бота")
    if (self.recense != ""):# and (not p.exists()): # рецензия есть, страницы нет
      wikipedia.output(self.page.titleWithoutNamespace(), toStdout = True)
      wikipedia.output(self.recense, toStdout = True)
      self.recense = u"\n\n== Автоматическая проверка статьи [["+self.page.title()+"]]==\r\n\r\n" + self.recense
      self.recense += u"<small>Рецензия составлена автоматическим ботом, проходящим отладку. Требуется внимание опытных участников для определения [[ВП:КЗ|значимости]], [[Википедия:Правила и указания#Содержание статьи|энциклопедичности содержания]] и прочего. ~~~~</small>"
      #p.put(self.recense,  u"Авто-рецензирование статей Инкубатора v0.2", minorEdit=False, botflag=True)
      p.put(p.get()+self.recense,  u"Авто-рецензирование статей Инкубатора v0.2", minorEdit=False, botflag=True)
# start point 
site = wikipedia.getSite()
cat=catlib.Category(site, u"Категория:Википедия:Инкубатор, Запросы авторов")
for page in cat.articles(3): # пошли проверять
  ih=inc_helper(page)
  ih.run()