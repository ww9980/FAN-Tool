"""
Under development
"""

from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

import os
import numpy as np
import config
import math
import cv2
import pytesseract

scaleRatio = 0
scaleUnit = 'unit';
MMode = 0
# 0 - drag and add (original)
# 2 - find h gap
# 3 - find v gap
# 4 - find scallop
# 5 - drag and draw a line
# 6 - drag and draw h line
# 7 - drag and draw v line

SCALE = 1
DELTA = 0
DDEPTH = cv2.CV_16S  ## to avoid overflow

style = 0
stylebg = 0

class MainGUI:
    def __init__(self, master):
        self.parent = master
        self.parent.title("Fan's automatic ANnotation tool (FAN tool) 1.2")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=False, height=False)

        # Initialize class variables
        self.img = None
        self.tkimg = None
        self.imageDir = ''
        self.imageDirPathBuffer = ''
        self.imageList = []
        self.imageTotal = 0
        self.imageCur = 0
        self.cur = 0
        self.bboxIdList = []
        self.bboxList = []
        self.bboxPointList = []
        self.dlineIdList = []
        self.dlinePtList = []
        self.dlineList = []
        self.melineIdList = []
        self.melineList = []
        self.melinePtList = []
        self.o1 = None
        self.o2 = None
        self.o3 = None
        self.o4 = None
        self.bboxId = None
        self.currLabel = None
        self.editbboxId = None
        self.currBboxColor = None
        self.zoomImgId = None
        self.zoomImg = None
        self.zoomImgCrop = None
        self.tkZoomImg = None
        self.scaleImg = None
        self.hl = None
        self.vl = None
        self.editPointId = None
        self.filename = None
        self.filenameBuffer = None
        self.objectLabelList = []
        self.EDIT = False

        # initialize mouse state
        self.STATE = {'x': 0, 'y': 0}
        self.STATE_COCO = {'click': 0}

        # ------------------ GUI ---------------------

        # Control Panel
        self.ctrlPanel = Frame(self.frame)
        self.ctrlPanel.grid(row=0, column=0, sticky=W + N)
        self.openBtn = Button(self.ctrlPanel, text='Open', command=self.open_image)
        self.openBtn.pack(fill=X, side=TOP)
        self.openDirBtn = Button(self.ctrlPanel, text='Open Dir', command=self.open_image_dir)
        self.openDirBtn.pack(fill=X, side=TOP)
        self.nextBtn = Button(self.ctrlPanel, text='Next ->', command=self.open_next)
        self.nextBtn.pack(fill=X, side=TOP)
        self.previousBtn = Button(self.ctrlPanel, text='<- Previous', command=self.open_previous)
        self.previousBtn.pack(fill=X, side=TOP)
        self.saveBtn = Button(self.ctrlPanel, text='Save', command=self.save)
        self.saveBtn.pack(fill=X, side=TOP)
        self.disp = Label(self.ctrlPanel, text='Coordinates:')
        self.disp.pack(fill=X, side=TOP)
        #self.addCocoBtn = Button(self.ctrlPanel, text="+", command=self.add_labels_coco)
        #self.addCocoBtn.pack(fill=X, side=TOP)
        self.zoomPanelLabel = Label(self.ctrlPanel, text="Precision View Panel")
        self.zoomPanelLabel.pack(fill=X, side=TOP)
        self.zoomcanvas = Canvas(self.ctrlPanel, width=150, height=150)
        self.zoomcanvas.pack(fill=X, side=TOP, anchor='center')
        self.cansize = Label(self.ctrlPanel, text='Canvas size:')
        self.cansize.pack(fill=X, side=TOP)
        self.scalecan = Canvas(self.ctrlPanel, width=60, height=150)
        self.scalecan.pack(fill=X, side=TOP, anchor='center')
        self.scalebar = Label(self.ctrlPanel, text='scale not set')
        self.scalebar.pack(fill=X, side=TOP)
        # self.scaleUnit = Label(self.ctrlPanel, text='No unit')
        # self.scaleUnit.pack(fill=X, side=TOP)
        self.scaleR = Label(self.ctrlPanel, text='----')
        self.scaleR.pack(fill=X, side=TOP)
        self.hlineBtn = Button(self.ctrlPanel, text='Auto H gap', command=self.h_line)
        self.hlineBtn.pack(fill=X, side=TOP)
        self.vlineBtn = Button(self.ctrlPanel, text='Auto V gap', command=self.v_line)
        self.vlineBtn.pack(fill=X, side=TOP)
        self.scallopBtn = Button(self.ctrlPanel, text='Auto scallop', command=self.scallop)
        self.scallopBtn.pack(fill=X, side=TOP)
        self.spacer1 = Label(self.ctrlPanel, text='----')
        self.spacer1.pack(fill=X, side=TOP)
        self.rectBtn = Button(self.ctrlPanel, text='Draw a rect. box', command=self.d_rect)
        self.rectBtn.pack(fill=X, side=TOP)
        self.dlineBtn = Button(self.ctrlPanel, text='Draw a line', command=self.d_line)
        self.dlineBtn.pack(fill=X, side=TOP)
        self.dhlineBtn = Button(self.ctrlPanel, text='H line', command=self.d_hline)
        self.dhlineBtn.pack(fill=X, side=TOP)
        self.dvlineBtn = Button(self.ctrlPanel, text='V line', command=self.d_vline)
        self.dvlineBtn.pack(fill=X, side=TOP)

        # Image Editing Region
        self.canvas = Canvas(self.frame, width=1024, height=768)
        self.canvas.grid(row=0, column=1, sticky=W + N)
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<Motion>", self.mouse_move, "+")
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
        self.parent.bind("<Key-Left>", self.open_previous)
        self.parent.bind("<Key-Right>", self.open_next)
        self.parent.bind("Escape", self.cancel_bbox)

        # Labels and Bounding Box Lists Panel
        self.listPanel = Frame(self.frame)
        self.listPanel.grid(row=0, column=2, sticky=W + N)
        self.listBoxNameLabel = Label(self.listPanel, text="List of Objects").pack(fill=X, side=TOP)
        self.objectListBox = Listbox(self.listPanel, width=40)
        self.objectListBox.pack(fill=X, side=TOP)
        self.delObjectBtn = Button(self.listPanel, text="Delete", command=self.del_bbox)
        self.delObjectBtn.pack(fill=X, side=TOP)
        self.clearAllBtn = Button(self.listPanel, text="Clear All", command=self.clear_bbox)
        self.clearAllBtn.pack(fill=X, side=TOP)
        #self.frameER = Frame(self.frame)
        #self.frameER.grid(row=0, column=2, sticky=W + N)
        self.classesNameLabel = Label(self.listPanel, text="====ER calc.====").pack(fill=X, side=TOP)
        self.classesNameLabel = Label(self.listPanel, text="Etch time (s): ").pack(fill=X, side=TOP)
        self.ERtime = Entry(self.listPanel, text="Enter time")
        #self.textBox.bind("", calcER)
        self.ERtime.pack(fill=X, side=TOP)
        self.calcERBtn = Button(self.listPanel, text="Calculate", command=self.calcER)
        self.calcERBtn.pack(fill=X, side=TOP)
        self.ERresult = Label(self.listPanel, text='----')
        self.ERresult.pack(fill=X, side=TOP)
        self.spacer2 = Label(self.listPanel, text='Anno. style:')
        self.spacer2.pack(fill=X, side=TOP)
        self.style0Btn = Button(self.listPanel, text="No annotation", command=self.style0)
        self.style0Btn.pack(fill=X, side=TOP)
        # self.style1Btn = Button(self.listPanel, text="1 Text", command=self.style1)
        # self.style1Btn.pack(fill=X, side=TOP)
        self.style2Btn = Button(self.listPanel, text="Text on block", command=self.style2)
        self.style2Btn.pack(fill=X, side=TOP)


        # STATUS BAR
        self.statusBar = Frame(self.frame, width=500)
        self.statusBar.grid(row=1, column=1, sticky=W + N)
        self.processingLabel = Label(self.statusBar, text="                      ")
        self.processingLabel.pack(side="left", fill=X)
        self.imageIdxLabel = Label(self.statusBar, text="                      ")
        self.imageIdxLabel.pack(side="right", fill=X)

    def open_image(self):
        self.filename = filedialog.askopenfilename(title="Select Image", filetypes=(("jpeg files", "*.jpg"),
                                                                                    ("all files", "*.*")))
        if not self.filename:
            return None
        self.filenameBuffer = self.filename
        self.load_image(self.filenameBuffer)

    def open_image_dir(self):
        self.imageDir = filedialog.askdirectory(title="Select Dataset Directory")
        if not self.imageDir:
            return None
        self.imageList = os.listdir(self.imageDir)
        self.imageList = sorted(self.imageList)
        self.imageTotal = len(self.imageList)
        self.filename = None
        self.imageDirPathBuffer = self.imageDir
        self.load_image(self.imageDirPathBuffer + '/' + self.imageList[self.cur])

    def load_image(self, file):
        self.img = Image.open(file)
        self.imageCur = self.cur + 1
        self.imageIdxLabel.config(text='  ||   Image Number: %d / %d' % (self.imageCur, self.imageTotal))
        # Resize to Pascal VOC format
        w, h = self.img.size
        self.cansize.config(text='Image size: %d, %d' % (w, h))
        if w >= h:
            baseW = 1024
            wpercent = (baseW / float(w))
            hsize = int((float(h) * float(wpercent)))
            self.img = self.img.resize((baseW, hsize), Image.BICUBIC)
        else:
            baseH = 768
            wpercent = (baseH / float(h))
            wsize = int((float(w) * float(wpercent)))
            self.img = self.img.resize((wsize, baseH), Image.BICUBIC)

        self.tkimg = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.clear_bbox()
        #Autoscale
        im = np.asarray(self.img)
        ima = im[690:720,0:200]
        self.tkScaleImg = ImageTk.PhotoImage(Image.fromarray(im[690:750,0:200]).resize((150, 60)))
        self.scalecan.create_image(0, 0, image=self.tkScaleImg, anchor=NW)
        ocr = pytesseract.image_to_string(ima)
        global scaleUnit
        print(ocr)
        print(ocr.split()[0])
        print(ocr.split()[1])
        self.scalebar.config(text='%s %s' % (ocr.split()[0], ocr.split()[1]))
        scaleUnit = ocr.split()[1]
        imt = im[720:750,0:200]
        imtg = cv2.cvtColor(imt,cv2.COLOR_BGR2GRAY)
        dst = cv2.cornerHarris(imtg,2,1,0.04)
        result = np.where(dst > 0.3 * np.amax(dst))
        listOfCordinates = list(zip(result[0], result[1]))
        loc = []
        for x,y in listOfCordinates:
            if x > 10 and x < 20:
                #print(x,y)
                loc.append([x,y])
        dist = (abs(loc[1][1]-loc[0][1])+abs(loc[3][1]-loc[2][1]))/2
        print(dist)
        global scaleRatio
        scaleRatio=dist/int(ocr.split()[0])
        print(scaleRatio)
        self.scaleR.config(text='%.2f px per %s' % (scaleRatio, scaleUnit))
        print('...')
        self.scalebar.config(text='Auto-scaled: ')
        
        
    def d_rect(self, event = None):
        global MMode
        MMode = 0
        
    def d_line(self, event = None):
        global MMode
        MMode = 5
        
    def h_line(self, event = None):
        global MMode
        MMode = 2
    
    def v_line(self, event = None):
        global MMode
        MMode = 3
    
    def scallop(self, event = None):
        global MMode
        MMode = 4
    
    def d_hline(self, event = None):
        global MMode
        MMode = 6
        
    def d_vline(self, event = None):
        global MMode
        MMode = 7
        
    def style0(self, event = None):
        global style
        style = 0
        
    def style1(self, event = None):
        global style
        style = 1
        
    def style2(self, event = None):
        global style
        style = 2
    
    def calcER(self, event = None):
        sel = self.objectListBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        seltext = self.objectListBox.get(idx)
        seltext = seltext.split(':')[1].strip()
        ERdepth = seltext.split(' ')[0].strip()
        ERunit = seltext.split(' ')[1].strip()
        Etime = self.ERtime.get().strip()
        ER = float(ERdepth)/float(Etime)
        ERmin = float(ERdepth)/float(Etime)*60
        self.ERresult.configure(text = "Result: " + str(ER) + ERunit + '/s, or ' + str(ERmin) + ERunit + '/min')

    def open_next(self, event=None):
        self.save()
        if self.cur < len(self.imageList):
            self.cur += 1
            self.load_image(self.imageDirPathBuffer + '/' + self.imageList[self.cur])
        self.processingLabel.config(text="                      ")
        self.processingLabel.update_idletasks()

    def open_previous(self, event=None):
        self.save()
        if self.cur > 0:
            self.cur -= 1
            self.load_image(self.imageDirPathBuffer + '/' + self.imageList[self.cur])
        self.processingLabel.config(text="                      ")
        self.processingLabel.update_idletasks()

    def save(self):
        if self.filenameBuffer is None:
            self.annotation_file = open('annotations/' + self.anno_filename, 'a')
            for idx, item in enumerate(self.bboxList):
                self.annotation_file.write(self.imageDirPathBuffer + '/' + self.imageList[self.cur] + ',' +
                                           ','.join(map(str, self.bboxList[idx])) + ',' + str(self.objectLabelList[idx])
                                           + '\n')
            self.annotation_file.close()
        else:
            self.annotation_file = open('annotations/' + self.anno_filename, 'a')
            for idx, item in enumerate(self.bboxList):
                self.annotation_file.write(self.filenameBuffer + ',' + ','.join(map(str, self.bboxList[idx])) + ','
                                           + str(self.objectLabelList[idx]) + '\n')
            self.annotation_file.close()

    def mouse_click(self, event):
        # Check if Updating BBox
        if self.canvas.find_enclosed(event.x - 5, event.y - 5, event.x + 5, event.y + 5):
            self.EDIT = True
            self.editPointId = int(self.canvas.find_enclosed(event.x - 5, event.y - 5, event.x + 5, event.y + 5)[0])
        else:
            self.EDIT = False

        # Set the initial point
        if self.EDIT:
            idx = self.bboxPointList.index(self.editPointId)
            self.editbboxId = self.bboxIdList[math.floor(idx/4.0)]
            self.bboxId = self.editbboxId
            pidx = self.bboxIdList.index(self.editbboxId)
            pidx = pidx * 4
            self.o1 = self.bboxPointList[pidx]
            self.o2 = self.bboxPointList[pidx + 1]
            self.o3 = self.bboxPointList[pidx + 2]
            self.o4 = self.bboxPointList[pidx + 3]
            if self.editPointId == self.o1:
                a, b, c, d = self.canvas.coords(self.o3)
            elif self.editPointId == self.o2:
                a, b, c, d = self.canvas.coords(self.o4)
            elif self.editPointId == self.o3:
                a, b, c, d = self.canvas.coords(self.o1)
            elif self.editPointId == self.o4:
                a, b, c, d = self.canvas.coords(self.o2)
            self.STATE['x'], self.STATE['y'] = int((a+c)/2), int((b+d)/2)
        else:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
    
    
    def mouse_drag(self, event):
        self.mouse_move(event)
        #print(MMode)
        if MMode == 0:
            self.rect(event)
            #Solid box
        if MMode == 4:
            #print('DASH!')
            self.rectdash(event)
            #dashline box
        if MMode == 5:
            self.fline(event)
            #Free line
        if MMode == 6:
            self.hline(event)
            #h line
        if MMode == 7:
            self.vline(event)
            #v line
        if MMode == 2:
            self.hdline(event)
            #h line
        if MMode == 3:
            self.vdline(event)
            #v line
    
    def rect(self, event):
        #self.mouse_move(event)
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "outline")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                       event.x, event.y,
                                                       width=2,
                                                       outline=self.currBboxColor)
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                       event.x, event.y,
                                                       width=2,
                                                       outline=self.currBboxColor)

    def rectdash(self, event):
        #self.mouse_move(event)
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "outline")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                       event.x, event.y,
                                                       width=2, dash = (3,5))
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                       event.x, event.y,
                                                       width=2, dash = (3,5))

    def fline(self, event):
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "fill")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, event.y, fill=self.currBboxColor)
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, event.y, width=2, fill=self.currBboxColor)

    def hline(self, event):
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "fill")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, self.STATE['y'], fill=self.currBboxColor)
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, self.STATE['y'], width=2, fill=self.currBboxColor)

    def hdline(self, event):
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "fill")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, self.STATE['y'], fill=self.currBboxColor, dash = (3,5))
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], event.x, self.STATE['y'], width=2, fill=self.currBboxColor, dash = (3,5))

    def vline(self, event):
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "fill")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], self.STATE['x'], event.y, fill=self.currBboxColor)
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], self.STATE['x'], event.y, width=2, fill=self.currBboxColor)

    def vdline(self, event):
        if self.bboxId:
            self.currBboxColor = self.canvas.itemcget(self.bboxId, "fill")
            self.canvas.delete(self.bboxId)
            self.canvas.delete(self.o1)
            self.canvas.delete(self.o2)
            self.canvas.delete(self.o3)
            self.canvas.delete(self.o4)
        if self.EDIT:
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], self.STATE['x'], event.y, fill=self.currBboxColor, dash = (3,5))
        else:
            self.currBboxColor = config.COLORS[len(self.bboxList) % len(config.COLORS)]
            self.bboxId = self.canvas.create_line(self.STATE['x'], self.STATE['y'], self.STATE['x'], event.y, width=2, fill=self.currBboxColor, dash = (3,5))

    def mouse_move(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        self.zoom_view(event)
        if self.tkimg:
            # Horizontal and Vertical Line for precision
            if self.hl:
                self.canvas.delete(self.hl)
            self.hl = self.canvas.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.canvas.delete(self.vl)
            self.vl = self.canvas.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
            # elif (event.x, event.y) in self.bboxBRPointList:
            #     pass

    def create_MeText(self, event, x1, x2, y1, y2 , dis, su):
        self.bboxId = self.canvas.create_text((x1+x2)/2, (y1+y2)/2,fill="darkblue",font="Arial 16 bold", text = '%d ' % (dis) + scaleUnit)
        self.dlineIdList.append(self.bboxId)
        self.BoundaryBox = self.canvas.create_rectangle(self.canvas.bbox(self.bboxId),fill="white")
        self.dlineIdList.append(self.BoundaryBox)
        self.canvas.tag_lower(self.BoundaryBox, self.bboxId)
        canvas.pack(fill=BOTH, expand=1)


    def mouse_release(self, event):
        try:
            labelidx = self.labelListBox.curselection()
            self.currLabel = self.labelListBox.get(labelidx)
        except:
            pass
        if self.EDIT:
            self.update_bbox()
            self.EDIT = False
        x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
        y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
        if MMode == 0 :
            #draw rect box around
            self.bboxList.append((x1, y1, x2, y2))
            o1 = self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="red")
            o2 = self.canvas.create_oval(x2 - 2, y1 - 2, x2 + 2, y1 + 2, fill="red")
            o3 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="red")
            o4 = self.canvas.create_oval(x1 - 2, y2 - 2, x1 + 2, y2 + 2, fill="red")
            self.bboxPointList.append(o1)
            self.bboxPointList.append(o2)
            self.bboxPointList.append(o3)
            self.bboxPointList.append(o4)
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            xd = abs(x1-x2)
            #print(xd)
            #print(scaleRatio)
            xd = xd/scaleRatio
            #print(xd)
            yd = abs(y1-y2)
            yd = yd/scaleRatio
            
            self.objectListBox.insert(END, '(%d, %d)->(%d, %d)' % (x1, y1, x2, y2) + ': W %d, H %d (' % (xd, yd) + scaleUnit + ')')
            self.objectListBox.itemconfig(len(self.bboxIdList) - 1,
                                      fg=self.currBboxColor)
            self.currLabel = None
            
        if MMode == 4 :
            #draw rect box around and find scallop
            top = Toplevel()
            top.title("Ops...")
            msg = Message(top, text='This function is not yet available...')
            msg.pack()
            button = Button(top, text="OK", command=top.destroy)
            button.pack()
            #Start of the main code
            self.bboxIdList.append(self.bboxId)
            o1 = self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="green")
            o2 = self.canvas.create_oval(x2 - 2, y1 - 2, x2 + 2, y1 + 2, fill="green")
            o3 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="green")
            o4 = self.canvas.create_oval(x1 - 2, y2 - 2, x1 + 2, y2 + 2, fill="green")
            self.bboxPointList.append(o1)
            self.bboxPointList.append(o2)
            self.bboxPointList.append(o3)
            self.bboxPointList.append(o4)
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            im = np.asarray(self.img)
            ima = im[min(y1,y2):max(y1,y2),min(x1,x2):max(x1,x2)]
            # TO BE CONT

        if MMode == 5:
            #free line draw mode
            #o1 = self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="red")
            #o2 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="red")
            self.dlineIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            xd = abs(x1-x2)
            xd = xd/scaleRatio
            yd = abs(y1-y2)
            yd = yd/scaleRatio
            dist = xd*xd + yd*yd
            dist= np.sqrt(dist)
            self.objectListBox.insert(END, 'Line (%d, %d)->(%d, %d)' % (x1, y1, x2, y2) + ': %d ' % (dist) + scaleUnit )
            #self.objectListBox.itemconfig(len(self.bboxIdList) - 1,
                                      #fg=self.currBboxColor)
            self.currLabel = None
            self.dlineList.append((x1, y1, x2, y2))
            if style == 1:
                self.bboxId = self.canvas.create_text((x1+x2)/2, (y1+y2)/2,fill="darkblue",font="Arial 16 bold",
                        text= '%d ' % (dist) + scaleUnit)
                self.dlineIdList.append(self.bboxId)
                canvas.pack(fill=BOTH, expand=1)
            if style == 2:
                self.create_MeText(event=None, x1=x1,x2=x2,y1=y1,y2=y2, dis=dist, su=scaleUnit)
        if MMode == 6:
            #h line draw mode
            #o1 = self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="red")
            #o2 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="red")
            self.dlineIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            xd = abs(x1-x2)
            xd = xd/scaleRatio
            self.objectListBox.insert(END, 'H line (%d->%d, %d)' % (x1, x2, y2) + ': %d ' % (xd) + scaleUnit )
            #self.objectListBox.itemconfig(len(self.bboxIdList) - 1,fg=self.currBboxColor)
            self.currLabel = None
            self.dlineList.append((x1, y1, x2, y2))
            if style == 1:
                self.bboxId = self.canvas.create_text((x1+x2)/2, (y1+y2)/2,fill="darkblue",font="Arial 16 bold",
                        text= '%d ' % (xd) + scaleUnit)
                self.dlineIdList.append(self.bboxId)
                canvas.pack(fill=BOTH, expand=1)
            if style == 2:
                self.create_MeText(event=None, x1=x1,x2=x2,y1=y1,y2=y2, dis=xd, su=scaleUnit)
        if MMode == 7:
            #v line draw mode
            #o1 = self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="red")
            #o2 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="red")
            self.dlineIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            yd = abs(y1-y2)
            yd = yd/scaleRatio
            self.objectListBox.insert(END, 'V line (%d, %d->%d)' % (x1, y1, y2) + ': %d ' % (yd) + scaleUnit )
            #self.objectListBox.itemconfig(len(self.bboxIdList) - 1,fg=self.currBboxColor)
            self.currLabel = None
            self.dlineList.append((x1, y1, x2, y2))
            if style == 1:
                self.bboxId = self.canvas.create_text((x1+x2)/2, (y1+y2)/2,fill="darkblue",font="Arial 16 bold",
                        text= '%d ' % (yd) + scaleUnit)
                self.dlineIdList.append(self.bboxId)
                canvas.pack(fill=BOTH, expand=1)
            if style == 2:
                self.create_MeText(event=None, x1=x1,x2=x2,y1=y1,y2=y2, dis=yd, su=scaleUnit)
        if MMode == 2:
            #h line draw & find mode
            #o2 = self.canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill="red")
            self.melineIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            self.currLabel = None
            im = np.asarray(self.img)
            graysrc = cv2.GaussianBlur(im, (3, 3), 0)
            ## gradient X ##
            gradx = cv2.Sobel(graysrc, DDEPTH, 1, 0, ksize=3, scale=SCALE, delta=DELTA)
            gradx = cv2.convertScaleAbs(gradx)
            ys = self.STATE['y']
            gradx = gradx[ys, min(x1,x2):max(x1,x2)]
            gradx[gradx < 150] =0
            posX = np.where(gradx)
            posX = posX[0]
            npd = np.diff(posX)
            maxp = npd.tolist().index(npd.max())
            xa = posX[maxp]
            xb = xa + npd.max()
            #print(xa)
            xd = npd.max()/scaleRatio
            xa = min(x1,x2) + xa
            xb = min(x1,x2) + xb
            self.objectListBox.insert(END, 'Auto H line (%d->%d, %d)' % (xa, xb, ys) + ': %d ' % (xd) + scaleUnit )
            self.bboxId = self.canvas.create_line(xa, ys, xb, ys, width=2, fill=self.currBboxColor)
            self.dlineIdList.append(self.bboxId)
        if MMode == 3:
            # V line draw & find mode
            self.melineIdList.append(self.bboxId)
            self.bboxId = None
            self.objectLabelList.append(str(self.currLabel))
            self.currLabel = None
            xs = self.STATE['x']
            im = np.asarray(self.img)
            graysrc = cv2.GaussianBlur(im, (3, 3), 0)
            ## gradient X ##
            gradx = cv2.Sobel(graysrc, DDEPTH, 1, 0, ksize=3, scale=SCALE, delta=DELTA)
            gradx = cv2.convertScaleAbs(gradx)
            gradx = gradx[min(y1,y2):max(y1,y2), xs]
            gradx[gradx < 130] =0
            posX = np.where(gradx)
            posX = posX[0]
            npd = np.diff(posX)
            maxp = npd.tolist().index(npd.max())
            ya = posX[maxp]
            yb = ya + npd.max()
            yd = npd.max()/scaleRatio
            ya = min(y1,y2) + ya
            yb = min(y1,y2) + yb
            self.objectListBox.insert(END, 'Auto V line (%d, %d->%d)' % (xs, ya, yb) + ': %d ' % (yd) + scaleUnit )
            self.bboxId = self.canvas.create_line(xs, ya, xs, yb, width=2, fill=self.currBboxColor)
            self.dlineIdList.append(self.bboxId)

    def zoom_view(self, event):
        try:
            if self.zoomImgId:
                self.zoomcanvas.delete(self.zoomImgId)
            self.zoomImg = self.img.copy()
            self.zoomImgCrop = self.zoomImg.crop(((event.x - 25), (event.y - 25), (event.x + 25), (event.y + 25)))
            self.zoomImgCrop = self.zoomImgCrop.resize((150, 150))
            self.tkZoomImg = ImageTk.PhotoImage(self.zoomImgCrop)
            self.zoomImgId = self.zoomcanvas.create_image(0, 0, image=self.tkZoomImg, anchor=NW)
            hl = self.zoomcanvas.create_line(0, 75, 150, 75, width=2)
            vl = self.zoomcanvas.create_line(75, 0, 75, 150, width=2)
        except:
            pass

    def update_bbox(self):
        idx = self.bboxIdList.index(self.editbboxId)
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.objectListBox.delete(idx)
        self.currLabel = self.objectLabelList[idx]
        self.objectLabelList.pop(idx)
        idx = idx*4
        self.canvas.delete(self.bboxPointList[idx])
        self.canvas.delete(self.bboxPointList[idx+1])
        self.canvas.delete(self.bboxPointList[idx+2])
        self.canvas.delete(self.bboxPointList[idx+3])
        self.bboxPointList.pop(idx)
        self.bboxPointList.pop(idx)
        self.bboxPointList.pop(idx)
        self.bboxPointList.pop(idx)

    def cancel_bbox(self, event):
        if self.STATE['click'] == 1:
            if self.bboxId:
                self.canvas.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def del_bbox(self):
        sel = self.objectListBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.canvas.delete(self.bboxIdList[idx])
        self.canvas.delete(self.bboxPointList[idx * 4])
        self.canvas.delete(self.bboxPointList[(idx * 4) + 1])
        self.canvas.delete(self.bboxPointList[(idx * 4) + 2])
        self.canvas.delete(self.bboxPointList[(idx * 4) + 3])
        self.bboxPointList.pop(idx * 4)
        self.bboxPointList.pop(idx * 4)
        self.bboxPointList.pop(idx * 4)
        self.bboxPointList.pop(idx * 4)
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.objectLabelList.pop(idx)
        self.objectListBox.delete(idx)

    def clear_bbox(self):
        for idx in range(len(self.bboxIdList)):
            self.canvas.delete(self.bboxIdList[idx])
        for idx in range(len(self.bboxPointList)):
            self.canvas.delete(self.bboxPointList[idx])
        for idx in range(len(self.dlineIdList)):
            self.canvas.delete(self.dlineIdList[idx])
        for idx in range(len(self.melineIdList)):
            self.canvas.delete(self.melineIdList[idx])
        self.objectListBox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.objectLabelList = []
        self.bboxPointList = []

    def add_label(self):
        if self.textBox.get() is not '':
            curr_label_list = self.labelListBox.get(0, END)
            curr_label_list = list(curr_label_list)
            if self.textBox.get() not in curr_label_list:
                self.labelListBox.insert(END, str(self.textBox.get()))
            self.textBox.delete(0, 'end')

    def del_label(self):
        labelidx = self.labelListBox.curselection()
        self.labelListBox.delete(labelidx)



if __name__ == '__main__':
    root = Tk()
    imgicon = PhotoImage(file='icon2.gif')
    root.tk.call('wm', 'iconphoto', root._w, imgicon)
    tool = MainGUI(root)
    root.mainloop()
