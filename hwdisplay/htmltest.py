from tkinterhtml import HtmlFrame
import tkinter as tk
from OpenGL.GL import *

from pyopengltk import OpenGLFrame

class frame(OpenGLFrame):

    def initgl(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.0,1.0,0.0,0.0)

        # setup projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        # setup identity model view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        
    def redraw(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        glBegin(GL_LINES)
        glColor3f(1.0,0.0,3.0)
        glVertex2f(200,100)
        glVertex2f(100,100)
        glVertex2f(100,50)
        glVertex2f(200,50)
        glEnd()
        glBegin(GL_POLYGON)
        glColor3f(1.0,0.0,0.0)
        glVertex2f(100,100)
        glVertex2f(200,100)
        glVertex2f(200,200)
        glVertex2f(100,200)
        glVertex2f(50,50)
        
        glEnd()
        glFlush()


if __name__=='__main__':

    root = tk.Tk()
    app = frame(root,width=500,height=500)
    app.pack(fill=tk.BOTH, expand=tk.YES)
    app.mainloop()



nop='''
import tkinter as tk

root = tk.Tk()
root.geometry("1024x600")

def on_click(param):
    print("lol {}".format(param))

#frame = HtmlFrame(root, horizontal_scrollbar="auto")
frame = HtmlFrame(root, horizontal_scrollbar="auto", vertical_scrollbar="auto")

html = """
<html>
<body style="background-color: #000000; color: #ffffff">
<button style="color: red; background-color: white" id="one" name="a">test</button>

<button style="color: green; background-color: white" id="two" name="b">test2</button>
<button style="color: blue; background-color: white" id="three" name="c">test3</button>

<a href="duckduckgo.com">ddg</a>
</body>
</html>
"""
frame.set_content(html)

frame.pack()



frame.bind("<Button-1>", on_click)

#issues: HtmlFrame not conforming to 1024x600 size. I possibly have to adjust root's grid size.

root.mainloop()
'''