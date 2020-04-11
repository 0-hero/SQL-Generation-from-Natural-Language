from tkinter import *

window = Tk()
window.title('Convert Text to SQL')
window.geometry('475x400')

# Main Heading

main_heading = Label(window, text='Enter a query in natural language', font=('Arial Bold', 24))
main_heading.grid(column = 0, row = 0)

# Text Input
txt = Entry(window,width=50)
txt.grid(column = 0, row = 1)
txt.focus()

# Output Query
qury = Label(window, text='Generated query will be displayed here\n Project by 17BCE2189 & 16BCE', font=('Ubuntu Mono Bold', 18))
qury.grid(column=0, row = 2)
def clicked():
    qury.configure(text=txt.get())

btn = Button(window, text='Convert to SQL', bg='white', fg='black', command=clicked)
btn.grid(column = 0, row = 3)
window.mainloop()