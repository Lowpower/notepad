# -*- coding:utf-8 -*-
__author__ = 'shengzhiqiang'
__email__ = 'szq123456123@gmail.com'
__date__ = '2015-5-30 13:48'

import sys, os
import configparser as parser
# import ctypes
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("UTF-8"))
CONFIG_FILE_PATH = "notepad.ini"

class Notepad(QtWidgets.QMainWindow):
    def __init__(self):
        self.judgeConfigFile()
        """全局变量"""
        # 剪切板
        self.clipboard = QtWidgets.QApplication.clipboard()
        # 上一次搜索内容
        self.lastSearchText = ""
        # 上一次替换内容
        self.lastReplaceSearchText = ""
        # 是否重置
        self.reset = False
        # 配置文件
        self.config = parser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH)

        QtWidgets.QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("无标题 - 记事本")
        self.setWindowIcon(QtGui.QIcon("images/notepad.png"))

        self.initEditText()

        self.createActions()
        self.createStatusBar()
        self.createMenubars()
        self.createToolBars()

        self.readSettings()

        self.text.document().contentsChanged.connect(self.documentWasModified)

        self.setCurrentFile('')

    def initEditText(self):
        # 设置编辑区
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.customContextMenu)
        self.setCentralWidget(self.text)

    def customContextMenu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.undoAction)
        menu.addSeparator()
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addAction(self.deleteAction)
        menu.addSeparator()
        menu.addAction(self.selectAllAction)
        menu.exec_(QtGui.QCursor.pos())

        return menu

    def documentWasModified(self):
        self.setWindowModified(self.text.document().isModified())
        if "" != self.text.toPlainText():
            self.findAction.setEnabled(True)
            self.findNextAction.setEnabled(True)
        else:
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

    def readSettings(self):
        # 宽度 高度
        width = getConfig(self.config, "Display", "width", "1000")
        height = getConfig(self.config, "Display", "height", "600")
        size = QtCore.QSize(int(width), int(height))

        # 屏幕位置
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        pos_x = getConfig(self.config, "Display", "x", (screen.width() - 1000) // 2)
        pos_y = getConfig(self.config, "Display", "y", (screen.height() - 600) // 2)
        pos = QtCore.QPoint(int(pos_x), int(pos_y))

        # 是否显示工具栏
        toolbar = getConfig(self.config, "Display", "toolbar", "True")

        # 是否自动换行
        wrapMode = getConfig(self.config, "TextEdit", "wrapmode", "True")

        # 字体
        fontFamile = getConfig(self.config, "TextEdit", "font", "Consolas")
        fontSize = getConfig(self.config, "TextEdit", "size", 14)
        fonts = QtGui.QFont(fontFamile, int(fontSize))

        if "True" == wrapMode:
            self.autoWrapAction.setIcon(QtGui.QIcon("images/check.png"))
            wrapMode = QtWidgets.QPlainTextEdit.WidgetWidth
        else:
            self.autoWrapAction.setIcon(QtGui.QIcon("images/check_no.png"))
            wrapMode = QtWidgets.QPlainTextEdit.NoWrap

        if "True" == toolbar:
            self.toolBar.show()
            self.toolBarAction.setIcon(QtGui.QIcon("images/check.png"))
        else:
            self.toolBar.hide()
            self.toolBarAction.setIcon(QtGui.QIcon("images/check_no.png"))

        self.resize(size)
        self.move(pos)
        self.text.setLineWrapMode(wrapMode)
        self.text.setFont(fonts)

    def resetSettings(self):
        # 宽度、高度
        writeConfig(self.config, "Display", "width", "1000")
        writeConfig(self.config, "Display", "height", "600")
        # 位置
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        writeConfig(self.config, "Display", "x", str((screen.width() - 1000) // 2))
        writeConfig(self.config, "Display", "y", str((screen.height() - 600) // 2))
        # 工具栏
        writeConfig(self.config, "Display", "toolbar", "True")
        # 自动换行
        writeConfig(self.config, "TextEdit", "wrapmode", "True")
        # 字体
        writeConfig(self.config, "TextEdit", "font", "Consolas")
        # 大小
        writeConfig(self.config, "TextEdit", "size", "14")

        # 回写
        self.config.write(open(CONFIG_FILE_PATH, "w"))

        QtWidgets.QMessageBox.information(self, "记事本", "重置成功，请重启记事本！")
        self.reset = True
        self.close()

    def writeSettings(self):
        # 宽度、高度
        writeConfig(self.config, "Display", "height", str(self.size().height()))
        writeConfig(self.config, "Display", "width", str(self.size().width()))
        # 位置
        writeConfig(self.config, "Display", "x", str(self.pos().x()))
        writeConfig(self.config, "Display", "y", str(self.pos().y()))
        # 工具栏
        writeConfig(self.config, "Display", "toolbar", str(not self.toolBar.isHidden()))
        # 自动换行
        writeConfig(self.config, "TextEdit", "wrapmode",
                    str(self.text.lineWrapMode() == QtWidgets.QPlainTextEdit.WidgetWidth))
        # 字体
        writeConfig(self.config, "TextEdit", "font", self.text.font().family())
        # 大小
        writeConfig(self.config, "TextEdit", "size", str(self.text.font().pointSize()))

        # 回写
        self.config.write(open(CONFIG_FILE_PATH, "w"))

    def judgeConfigFile(self):
        if not os.path.exists(CONFIG_FILE_PATH):
            f = open(CONFIG_FILE_PATH, mode="w", encoding="UTF-8")
            f.close()

    def createActions(self):
        self.newAction = QtWidgets.QAction(QtGui.QIcon('images/new.png'), "&新建", self,
                                           shortcut=QtGui.QKeySequence.New, statusTip="创建文件",
                                           triggered=self.newFile)

        self.openAction = QtWidgets.QAction(QtGui.QIcon('images/open.png'), "&打开...",
                                            self, shortcut=QtGui.QKeySequence.Open,
                                            statusTip="打开文件", triggered=self.openFileEvent)

        self.saveAction = QtWidgets.QAction(QtGui.QIcon('images/save.png'), "&保存", self,
                                            shortcut=QtGui.QKeySequence.Save,
                                            statusTip="保存文件", triggered=self.save)

        self.saveAsAction = QtWidgets.QAction(QtGui.QIcon('images/save.png'), "另存为...", self,
                                              shortcut=QtGui.QKeySequence.SaveAs,
                                              statusTip="另存文件",
                                              triggered=self.saveAs)

        self.printAction = QtWidgets.QAction(QtGui.QIcon('images/print.png'), "打印...", self,
                                             shortcut=QtGui.QKeySequence.Print,
                                             statusTip="打印文件",
                                             triggered=self.printText)

        self.exitAction = QtWidgets.QAction(QtGui.QIcon('images/exit.png'), "退出", self, shortcut="Ctrl+Q",
                                            statusTip="退出程序", triggered=self.close)

        self.undoAction = QtWidgets.QAction(QtGui.QIcon('images/undo.png'), "撤销", self,
                                            shortcut=QtGui.QKeySequence.Undo,
                                            statusTip="撤销编辑",
                                            triggered=self.text.undo)

        self.cutAction = QtWidgets.QAction(QtGui.QIcon('images/cut.png'), "剪切", self,
                                           shortcut=QtGui.QKeySequence.Cut,
                                           statusTip="剪切选中的文本",
                                           triggered=self.text.cut)

        self.copyAction = QtWidgets.QAction(QtGui.QIcon('images/copy.png'), "复制", self,
                                            shortcut=QtGui.QKeySequence.Copy,
                                            statusTip="复制选中的文本",
                                            triggered=self.text.copy)

        self.pasteAction = QtWidgets.QAction(QtGui.QIcon('images/paste.png'), "粘贴", self,
                                             shortcut=QtGui.QKeySequence.Paste,
                                             statusTip="粘贴剪切板的文本",
                                             triggered=self.text.paste)

        self.clearAction = QtWidgets.QAction(QtGui.QIcon('images/clear.png'), "清空剪切板", self,
                                             statusTip="清空剪切板",
                                             triggered=self.clearClipboard)

        self.deleteAction = QtWidgets.QAction(QtGui.QIcon("images/delete.png"), "删除", self,
                                              statusTip="删除选中的文本",
                                              triggered=self.delete)

        self.findAction = QtWidgets.QAction(QtGui.QIcon("images/find.png"), "查找", self,
                                            statusTip="查找文本", triggered=self.findText, shortcut=QtGui.QKeySequence.Find)

        self.findNextAction = QtWidgets.QAction(QtGui.QIcon("images/find.png"), "查找下一个", self,
                                                statusTip="查找文本", triggered=self.findNextText,
                                                shortcut=QtGui.QKeySequence.FindNext)

        self.replaceAction = QtWidgets.QAction(QtGui.QIcon("images/replace.png"), "替换", self,
                                               statusTip="替换文本", triggered=self.replaceText,
                                               shortcut=QtGui.QKeySequence.Replace)

        self.selectAllAction = QtWidgets.QAction(QtGui.QIcon('images/selectAll.png'), "全选", self,
                                                 shortcut=QtGui.QKeySequence.SelectAll,
                                                 statusTip="全选",
                                                 triggered=self.text.selectAll)

        self.dateAction = QtWidgets.QAction(QtGui.QIcon("images/date.png"), "时间/日期", self, shortcut="F5",
                                            statusTip="插入时间/日期",
                                            triggered=self.dateEvent)

        self.autoWrapAction = QtWidgets.QAction(QtGui.QIcon("images/check.png"), "自动换行", self,
                                                statusTip="设置自动换行",
                                                triggered=self.setWrap)

        self.fontAction = QtWidgets.QAction(QtGui.QIcon("images/font.png"), "字体", self,
                                            statusTip="设置字体", triggered=self.setFont_)

        self.toolBarAction = QtWidgets.QAction(QtGui.QIcon("images/check.png"), "工具栏", self,
                                               statusTip="工具栏",
                                               triggered=self.toggleToolBar)

        self.resetAction = QtWidgets.QAction(QtGui.QIcon("images/reset.png"), "重置", self,
                                             statusTip="重置所有属性",
                                             triggered=self.resetSettings)

        self.aboutAction = QtWidgets.QAction(QtGui.QIcon("images/about.png"), "关于", self, triggered=self.about)

        self.aboutQtAction = QtWidgets.QAction(QtGui.QIcon("images/qt.png"), "关于Qt", self,
                                               triggered=QtWidgets.QApplication.instance().aboutQt)

        self.undoAction.setEnabled(False)
        self.cutAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.deleteAction.setEnabled(False)
        if "" == self.clipboard.text():
            self.pasteAction.setEnabled(False)
            self.clearAction.setEnabled(False)
        if "" == self.text.toPlainText():
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

        self.text.undoAvailable.connect(self.undoAction.setEnabled)
        self.text.copyAvailable.connect(self.cutAction.setEnabled)
        self.text.copyAvailable.connect(self.copyAction.setEnabled)
        self.text.copyAvailable.connect(self.deleteAction.setEnabled)

        self.clipboard.dataChanged.connect(self.enabledSomeActionByClipboard)

    def enabledSomeActionByClipboard(self):
        if ("" != self.clipboard.text()):
            self.pasteAction.setEnabled(True)
            self.clearAction.setEnabled(True)

    def clearClipboard(self):
        self.clipboard.clear()
        self.pasteAction.setEnabled(False)
        self.clearAction.setEnabled(False)

    def createStatusBar(self):
        self.statusBar().showMessage("准备就绪")

    def createMenubars(self):
        file = self.menuBar().addMenu("文件")
        file.addAction(self.newAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)
        file.addAction(self.saveAsAction)
        file.addSeparator()
        file.addAction(self.printAction)
        file.addSeparator()
        file.addAction(self.exitAction)

        edit = self.menuBar().addMenu("编辑")
        edit.addAction(self.undoAction)
        edit.addSeparator()
        edit.addAction(self.cutAction)
        edit.addAction(self.copyAction)
        edit.addAction(self.pasteAction)
        edit.addAction(self.clearAction)
        edit.addAction(self.deleteAction)
        edit.addSeparator()
        edit.addAction(self.findAction)
        edit.addAction(self.findNextAction)
        edit.addAction(self.replaceAction)
        edit.addSeparator()
        edit.addAction(self.selectAllAction)
        edit.addAction(self.dateAction)

        style = self.menuBar().addMenu("格式")
        style.addAction(self.autoWrapAction)
        style.addAction(self.fontAction)

        view = self.menuBar().addMenu("查看")
        view.addAction(self.toolBarAction)
        view.addAction(self.resetAction)

        help = self.menuBar().addMenu("帮助")
        help.addAction(self.aboutAction)
        help.addAction(self.aboutQtAction)

    def createToolBars(self):
        self.toolBar = self.addToolBar("")
        self.toolBar.addAction(self.newAction)
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.cutAction)
        self.toolBar.addAction(self.copyAction)
        self.toolBar.addAction(self.pasteAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.clearAction)

    def newFile(self):
        if self.maybeSave():
            self.text.clear()

    def maybeSave(self):
        if self.text.document().isModified():
            ret = self.tip()

            if 0 == ret:
                return self.save()

            if 2 == ret:
                return False

        return True

    def openFileEvent(self):
        # 如果先前被打开的文件已被修改，需要提示
        if self.maybeSave():
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self)
            file = QtCore.QFile(fileName)
            if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                QtWidgets.QMessageBox.warning(self, "记事本",
                                              "文件%s不能被读取:\n%s." % (fileName, file.errorString()))
                return

            inf = QtCore.QTextStream(file)
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.text.setPlainText(inf.readAll())
            QtWidgets.QApplication.restoreOverrideCursor()

            self.setCurrentFile(fileName)
            self.statusBar().showMessage("文件读取成功", 2000)

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.text.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = '未命名.txt'

        self.setWindowTitle("%s[*] - 记事本" % shownName)

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)
        else:
            return self.saveAs()

    def saveAs(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)

        return False

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self, "记事本",
                                          "文件%s不能被写入:\n%s." % (fileName, file.errorString()))
            return False

        outf = QtCore.QTextStream(file)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outf << self.text.toPlainText()
        QtWidgets.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("写入文件成功", 2000)
        return True

    def closeEvent(self, event):
        if not self.maybeSave():
            event.ignore()
        else:
            if not self.reset:
                self.writeSettings()
            event.accept()

    def tip(self, title="记事本", content="文件已被修改，是否保存？"):
        alertBox = QtWidgets.QMessageBox(self)
        saveButton = alertBox.addButton("保存", QtWidgets.QMessageBox.ActionRole)
        unSaveButton = alertBox.addButton("不保存", QtWidgets.QMessageBox.ActionRole)
        cancelButton = alertBox.addButton("取消", QtWidgets.QMessageBox.ActionRole)

        alertBox.setWindowTitle(title)
        alertBox.setText(content)
        alertBox.exec_()
        button = alertBox.clickedButton()

        if saveButton == button:
            return 0
        elif unSaveButton == button:
            return 1
        elif cancelButton == button:
            return 2
        else:
            return -1;

    def dateEvent(self):
        """插入时间"""
        current = QtCore.QDateTime.currentDateTime();
        current = current.toString("yyyy-MM-dd hh:mm");
        self.text.insertPlainText(current)

    def printText(self):
        document = self.text.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("打印成功", 2000)

    def delete(self):
        cursor = self.text.textCursor()
        if not cursor.isNull():
            cursor.removeSelectedText()
            self.statusBar().showMessage("删除成功", 2000)

    def findText(self):
        self.displayFindDialog()

    def findNextText(self):
        if "" == self.lastSearchText:
            self.displayFindDialog()
        else:
            self.searchText()

    def displayFindDialog(self):
        self.findDialog = QtWidgets.QDialog(self)

        label = QtWidgets.QLabel("查找内容:")
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText(self.lastSearchText)
        label.setBuddy(self.lineEdit)

        self.findButton = QtWidgets.QPushButton("查找下一个")
        self.findButton.setDefault(True)
        self.findButton.clicked.connect(self.searchText)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(self.findButton, QtWidgets.QDialogButtonBox.ActionRole)

        topLeftLayout = QtWidgets.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.setRowStretch(2, 1)
        self.findDialog.setLayout(mainLayout)

        self.findDialog.setWindowTitle("查找")
        self.findDialog.show()

    def searchText(self):
        # 获取光标位置
        # 从光标位置处开始搜索
        cursor = self.text.textCursor()
        findIndex = cursor.anchor()
        text = self.lineEdit.text()
        content = self.text.toPlainText()
        length = len(text)

        self.lastSearchText = text
        index = content.find(text, findIndex)

        if -1 == index:
            errorDialog = QtWidgets.QMessageBox(self)
            errorDialog.addButton("取消", QtWidgets.QMessageBox.ActionRole)

            errorDialog.setWindowTitle("记事本")
            errorDialog.setText("找不到\"%s\"." % text)
            errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
            errorDialog.exec_()
        else:
            start = index

            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + length)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceText(self):
        replaceDialog = QtWidgets.QDialog(self)

        replaceLabel = QtWidgets.QLabel("替换内容:")
        self.replaceText = QtWidgets.QLineEdit()
        self.replaceText.setText(self.lastReplaceSearchText)
        replaceLabel.setBuddy(self.replaceText)

        replaceToLabel = QtWidgets.QLabel("替换为  :")
        self.replaceToText = QtWidgets.QLineEdit()
        replaceToLabel.setBuddy(self.replaceToText)

        findNextButton = QtWidgets.QPushButton("查找下一个")
        findNextButton.setDefault(True)
        replaceButton = QtWidgets.QPushButton("替换")
        replaceAllButton = QtWidgets.QPushButton("全部替换")
        cancelAllButton = QtWidgets.QPushButton("取消")

        # 按钮事件绑定
        findNextButton.clicked.connect(lambda: self.replaceOrSearch(False))
        cancelAllButton.clicked.connect(replaceDialog.close)
        replaceButton.clicked.connect(lambda: self.replaceOrSearch(True))
        replaceAllButton.clicked.connect(self.replaceAllText)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(findNextButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceAllButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelAllButton, QtWidgets.QDialogButtonBox.ActionRole)

        topLeftLayout = QtWidgets.QHBoxLayout()

        topLeftLayout.addWidget(replaceLabel)
        topLeftLayout.addWidget(self.replaceText)

        topLeftLayout2 = QtWidgets.QHBoxLayout()
        topLeftLayout2.addWidget(replaceToLabel)
        topLeftLayout2.addWidget(self.replaceToText)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addLayout(topLeftLayout2)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.setRowStretch(2, 1)
        replaceDialog.setLayout(mainLayout)

        replaceDialog.setWindowTitle("替换")
        replaceDialog.show()

    def replaceOrSearch(self, isReplace):
        # 获取光标位置
        # 从光标位置处开始搜索
        cursor = self.text.textCursor()
        findIndex = cursor.anchor()
        text = self.replaceText.text()
        content = self.text.toPlainText()
        length = len(text)
        index = content.find(text, findIndex)
        self.lastReplaceSearchText = text
        if -1 == index:
            errorDialog = QtWidgets.QMessageBox(self)
            errorDialog.addButton("取消", QtWidgets.QMessageBox.ActionRole)

            errorDialog.setWindowTitle("记事本")
            errorDialog.setText("找不到\"%s\"." % text)
            errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
            errorDialog.exec_()
        else:
            start = index
            if isReplace:
                toReplaceText = self.replaceToText.text()
                prefix = content[0:start]
                postfix = content[start + length:]
                newText = prefix + toReplaceText + postfix
                self.text.setPlainText(newText)
                length = len(toReplaceText)
                self.text.document().setModified(True)

            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + length)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceAllText(self):
        text = self.replaceText.text()
        content = self.text.toPlainText()
        toReplaceText = self.replaceToText.text()
        content = content.replace(text, toReplaceText)
        self.text.setPlainText(content)
        self.text.document().setModified(True)

    def setWrap(self):
        mode = self.text.lineWrapMode()
        if 1 == mode:
            # 自动换行
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
            self.autoWrapAction.setIcon(QtGui.QIcon("images/check_no.png"))
        else:
            # 不自动换行
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
            self.autoWrapAction.setIcon(QtGui.QIcon("images/check.png"))

    def toggleToolBar(self):
        if self.toolBar.isHidden():
            self.toolBar.show()
            self.toolBarAction.setIcon(QtGui.QIcon("images/check.png"))
        else:
            self.toolBar.hide()
            self.toolBarAction.setIcon(QtGui.QIcon("images/check_no.png"))

    def setFont_(self):
        font, ok = QtWidgets.QFontDialog.getFont(QtGui.QFont(self.text.toPlainText()), self)
        if ok:
            self.text.setFont(font)

    def about(self):
        QtWidgets.QMessageBox.about(self, "关于记事本",
                                    "这是仿照Windows系统自带记事本(Nodepad)应用写的一个基于Python_3.4.2 + PyQt_5.4.1的记事本\r\n"
                                    "作者：LowPower\r\n")


def getConfig(config, selection, option, default=""):
    if config is None:
        return default
    else:
        try:
            return config.get(selection, option)
        except:
            return default


def writeConfig(config, selection, option, value):
    if not config.has_section(selection):
        config.add_section(selection)

    config.set(selection, option, value)

# 设置Windows任务栏的图标
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("nodepad")
app = QtWidgets.QApplication(sys.argv)
notepad = Notepad()
notepad.show()
app.exec_()
