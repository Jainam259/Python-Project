# Text to Convert HandWritting

import pywhatkit as pw

txt = """Python is a high-level, interpreted, general-purpose programming language.
Created by Guido van Rossum in 1991.
It is easy to read, write, and learn because of its simple syntax (similar to English).
Widely used in web development, data science, artificial intelligence, machine learning, automation, software development, and more."""

pw.text_to_handwriting(txt,'handwritting.png',[0,0,138])
print("Text to Convert Handwriting Successfully.")