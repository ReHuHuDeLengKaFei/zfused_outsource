#coding:utf-8
import maya.cmds as cmds
import string
import colliderGroup
reload(colliderGroup)

class Ui(object):
    def showUi(self):
        self.windowName = 'ModelArrange'
        if cmds.window(self.windowName, exists = True) == True:
            cmds.deleteUI(self.windowName, window = True)
        if cmds.windowPref(self.windowName, exists = True) == True:
            cmds.windowPref(self.windowName, remove = True)
        self.creatTWindow = cmds.window(self.windowName, title = self.windowName, sizeable = True, tlc = [280, 430])
        self.windowFoL = cmds.formLayout(parent = self.creatTWindow)
        self.creatFrL = cmds.frameLayout(parent = self.windowFoL, label = 'Create Tree')
        self.creatTRCL = cmds.rowColumnLayout(parent = self.creatFrL, numberOfColumns = 5, columnSpacing = [(1, 8), (2, 7), (3, 7), (4, 6)])
        cmds.text(label='Name:', parent = self.creatTRCL)
        self.textFG = cmds.textField(parent = self.creatTRCL, enterCommand = lambda *args: self.creatTree())

        self.typeOM = cmds.optionMenu(parent = self.creatTRCL)        
        cmds.menuItem(parent = self.typeOM, label = 'Characters')
        cmds.menuItem(parent = self.typeOM, label = 'Props')
        cmds.menuItem(parent = self.typeOM, label = 'Scene')
        cmds.menuItem(parent = self.typeOM, label = 'MeshGen')
        cmds.optionMenu(self.typeOM,e=1,cc=lambda *args: self.judgeWin())
        cmds.button(parent = self.creatTRCL, label = 'Create', width = 87, command = lambda *args: self.creatTree())
        cmds.formLayout(parent = self.creatTRCL,w=11)
        self.setNameSpace()
        self.characterComp()
        self.GRPExists()
    def characterComp(self):
        self.controlFrL = cmds.frameLayout(parent = self.windowFoL, label = 'Control', collapsable = True, collapse = True)
        groupFrL = cmds.frameLayout(parent = self.controlFrL, label = 'Geometry Group', collapsable = True, collapse = True)
        controlFoL = cmds.formLayout(parent = groupFrL)
        cmds.formLayout(self.windowFoL, edit = True, attachForm = [
        (self.creatFrL, 'top', 5),
        (self.creatFrL, 'left', 5),
        (self.creatFrL, 'right', 5),
        (self.controlFrL, 'left', 5),
        (self.controlFrL, 'right', 5),
        (self.controlFrL, 'bottom', 5)
        ],
        attachControl = [
        (self.controlFrL, 'top', 5, self.creatFrL)
        ])
        cmds.showWindow(self.creatTWindow)
        self.controlFoL = controlFoL
        self.multipleGRP()
        self.Daniel_modleAss()
        textExist = cmds.textField(self.textFG, query = True, text = True)
        cmds.select(cl=1)
    def propComp(self):
        controlFrL = cmds.frameLayout(parent = self.windowFoL, label = 'Control', collapsable = True, collapse = False)
        porpAssBtn = cmds.button('propBtn',l='geometry',p=controlFrL,c=lambda *args: self.snakeCommand(porpAssBtn))
        previewBtn = cmds.button('proppreviewBtn',l='preview',p=controlFrL,c=lambda *args: self.snakeCommand(previewBtn))
        cmds.formLayout(self.windowFoL, edit = True, attachForm = [
        (self.creatFrL, 'top', 5),
        (self.creatFrL, 'left', 5),
        (self.creatFrL, 'right', 5),
        (controlFrL, 'left', 5),
        (controlFrL, 'right', 5),
        (controlFrL, 'bottom', 5)
        ],
        attachControl = [
        (controlFrL, 'top', 5, self.creatFrL)
        ])        
        cmds.showWindow(self.creatTWindow)
        self.controlFrL = controlFrL      
        
                
    def Daniel_modleAss(self):
        creatTRCL = cmds.rowColumnLayout(parent = self.controlFoL, numberOfColumns = 2, columnSpacing = [(1, 10)])
        f = cmds.formLayout(nd=100,parent = creatTRCL)
        hairAssBut = cmds.button('hairBut',l="hair",w=100,h=30,bgc = [0.9,0.4,0],command = lambda *args: self.snakeCommand(hairAssBut))
        beardAssBut = cmds.button('beardBut',l='beard',w=50,h=50,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(beardAssBut))
        headBut = cmds.button('head',l='head',w=80,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(headBut))
        r_earAssBut = cmds.button('r_earBut',l='r_ear',w=50,h=60,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(r_earAssBut))
        l_earAssBut = cmds.button('l_earBut',l='l_ear',w=50,h=60,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(l_earAssBut))
        r_elbowAssBut = cmds.button('r_elbowBut',l='r_brow',w=60,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(r_elbowAssBut))
        l_elbowAssBut = cmds.button('l_elbowBut',l='l_brow',w=60,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(l_elbowAssBut))
        r_eyeAssBut = cmds.button('r_eyeBut',l='r_eye',w=60,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(r_eyeAssBut))
        l_eyeAssBut = cmds.button('l_eyeBut',l='l_eye',w=60,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(l_eyeAssBut))
        r_upLassAssBut = cmds.button('r_upLassBut',l='r_upLash',w=60,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.lashCommand_R())
        l_upLassAssBut = cmds.button('l_upLassBut',l='l_upLash',w=60,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.lashCommand_L())
        r_lowLassAssBut = cmds.button('r_lowLassBut',l='r_lowLash',w=60,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.lashCommand_R())
        l_lowLassAssBut =cmds.button('l_lowLassBut',l='l_lowLash',w=60,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.lashCommand_L())
        upTeeAssBut = cmds.button('up_teeBut',l='upteeth',w=100,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(upTeeAssBut))
        tongueAssBut = cmds.button('tongueBut',l='tongue',w=100,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(tongueAssBut))
        lowTeeAssBut = cmds.button('low_teeBut',l='lowteeth',w=100,h=20,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(lowTeeAssBut))
        nonnasalityBut = cmds.button('n_lity',l='nonnasality',w=100,h=20,bgc=[0.9,0.4,0.0],command = lambda *args: self.snakeCommand(nonnasalityBut))
        bodyBut = cmds.button('bodyBut',l='body',w=80,h=50,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(bodyBut))
        bodyassBut = cmds.button('bodyassBut',l='bodyass',w=80,h=40,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(bodyassBut))
        closeeyeBut = cmds.button('closeeyeBut',l='closeeye',w=80,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(closeeyeBut))
        openeyeBut = cmds.button('openeyeBut',l='openeye',w=80,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(openeyeBut))
        
        r_armAssBut = cmds.button('r_armBut',l='r_arm',w=50,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(r_armAssBut))
        l_armAssBut = cmds.button('l_armBut',l='l_arm',w=50,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(l_armAssBut))
        r_handAssBut = cmds.button('r_handBut',l='r_hand',w=50,h=40,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(r_handAssBut))
        l_handAssBut = cmds.button('l_handBut',l='l_hand',w=50,h=40,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(l_handAssBut))
        r_legAssBut = cmds.button('r_legBut',l='r_leg',w=40,h=40,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(r_legAssBut))
        l_legAssBut = cmds.button('l_legBut',l='l_leg',w=40,h=40,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(l_legAssBut))
        r_footAssBut = cmds.button('r_footBut',l='r_foot',w=50,h=40,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(r_footAssBut))
        l_footAssBut = cmds.button('l_footBut',l='l_foot',w=50,h=40,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(l_footAssBut))
        r_shoeAssBut = cmds.button('r_shoeBut',l='r_shoe',w=50,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(r_shoeAssBut))
        l_shoeAssBut = cmds.button('l_shoeBut',l='l_shoe',w=50,h=20,bgc=[0.9,0.4,0],command = lambda *args: self.snakeCommand(l_shoeAssBut))
        
        headassBut = cmds.button('headBut',l='headass',parent = f,w=100,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(headassBut))
        clothBut = cmds.button('clothBut',l='cloth',parent = f,w=35,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(clothBut))

        previewBut = cmds.button('previewBut',l='preview',parent = f,w=50,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(previewBut))
        deformBut = cmds.button('deformBut',l='deform',parent = f,w=41,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(deformBut))

        solverBut = cmds.button('solvermodelBut',l='solvermodel',parent = f,w=70,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.snakeCommand(solverBut))
        colliderBut = cmds.button('collider',l='collider',parent = f,w=40,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.colliderApp())
        disBut = cmds.button('disBut',l='display/hide',parent = f,w=65,h=30,bgc=[0.9,0.9,0.9],command = lambda *args: self.setDisplay())

        cmds.formLayout(f,e=1,attachForm=[
        (hairAssBut,'left',110),
        (hairAssBut,'top',0),
        (headBut,'left',120),
        (headBut,'top',31),
        (r_earAssBut,'left',10),
        (r_earAssBut,'top',81),
        (l_earAssBut,'left',265),
        (l_earAssBut,'top',81),
        (r_elbowAssBut,'left',70),
        (r_elbowAssBut,'top',61),
        (l_elbowAssBut,'left',190),
        (l_elbowAssBut,'top',61),
        (r_eyeAssBut,'left',70),
        (r_eyeAssBut,'top',101),
        (r_upLassAssBut,'left',70),
        (r_upLassAssBut,'top',81),
        (r_lowLassAssBut,'left',70),
        (r_lowLassAssBut,'top',121),
        (l_upLassAssBut,'left',190),
        (l_upLassAssBut,'top',81),
        (l_lowLassAssBut,'left',190),
        (l_lowLassAssBut,'top',121),
        (l_eyeAssBut,'left',190),
        (l_eyeAssBut,'top',101),
        (beardAssBut,'left',265),
        (beardAssBut,'top',181),
        (upTeeAssBut,'left',110),
        (upTeeAssBut,'top',181),
        (tongueAssBut,'left',110),
        (tongueAssBut,'top',201),
        (lowTeeAssBut,'left',110),
        (lowTeeAssBut,'top',221),
        (nonnasalityBut,'left',110),
        (nonnasalityBut,'top',241),
        (r_armAssBut,'left',65),
        (r_armAssBut,'top',291),
        (bodyBut,'left',120),
        (bodyBut,'top',311),
        (bodyassBut,'left',120),
        (bodyassBut,'top',371),
        
        (closeeyeBut,'left',0),
        (closeeyeBut,'top',181),
        (openeyeBut,'left',0),
        (openeyeBut,'top',221),
        (l_armAssBut,'left',205),
        (l_armAssBut,'top',291),
        (r_handAssBut,'left',30),
        (r_handAssBut,'top',371),
        (l_handAssBut,'left',240),
        (l_handAssBut,'top',371),
        (r_legAssBut,'left',120),
        (r_legAssBut,'top',426),
        (l_legAssBut,'left',160),
        (l_legAssBut,'top',426),
        (r_footAssBut,'left',100),
        (r_footAssBut,'top',541),
        (l_footAssBut,'left',170),
        (l_footAssBut,'top',541),
        (r_shoeAssBut,'left',50),
        (r_shoeAssBut,'top',561),
        (l_shoeAssBut,'left',220),
        (l_shoeAssBut,'top',561),
        (headassBut,'left',210),
        (headassBut,'top',0),
        (clothBut,'left',0),
        (clothBut,'bottom',0),
        (previewBut,'left',38),
        (previewBut,'bottom',0),
        (deformBut,'left',91),
        (deformBut,'bottom',0),
        (solverBut,'left',135),
        (solverBut,'bottom',0),
        (colliderBut,'left',208),
        (colliderBut,'bottom',0),
        (disBut,'left',250),
        (disBut,'bottom',0)
        ])    
        self.hairAssBut = hairAssBut
        self.beardAssBut = beardAssBut
        self.headBut = headBut
        self.r_earAssBut = r_earAssBut
        self.l_earAssBut = l_earAssBut
        self.r_elbowAssBut = r_elbowAssBut
        self.l_elbowAssBut = l_elbowAssBut
        self.r_eyeAssBut = r_eyeAssBut
        self.l_eyeAssBut = l_eyeAssBut
        self.r_upLassAssBut = r_upLassAssBut
        self.l_upLassAssBut = l_upLassAssBut    
        self.r_lowLassAssBut = r_lowLassAssBut
        self.l_lowLassAssBut = l_lowLassAssBut
        self.upTeeAssBut = upTeeAssBut
        self.tongueAssBut = tongueAssBut
        self.lowTeeAssBut = lowTeeAssBut
        self.nonnasalityBut = nonnasalityBut
        self.r_armAssBut = r_armAssBut
        self.bodyBut = bodyBut
        self.bodyassBut = bodyassBut
        self.l_armAssBut = l_armAssBut
        self.r_handAssBut = r_handAssBut
        self.l_handAssBut = l_handAssBut
        self.r_legAssBut = r_legAssBut
        self.l_legAssBut = l_legAssBut
        self.r_footAssBut = r_footAssBut
        self.l_footAssBut = l_footAssBut
        self.r_shoeAssBut = r_shoeAssBut
        self.l_shoeAssBut = l_shoeAssBut   
        self.closeeyeBut = closeeyeBut
        self.openeyeBut = openeyeBut
        self.colliderBut = colliderBut

    def creatTree(self):
        typeOM = self.typeOM
        textFG = self.textFG
        confirmD = ''
        typeOMI = cmds.optionMenu(typeOM, query = True, select = True)
        treeName = cmds.textField(textFG, query = True, text = True)
        if treeName=='':
            cmds.confirmDialog(message=u'请输入资产名字！\n\n命名只能由【英文】、【数字】和【下划】线构成，并且首字母必须是英文。\n请注意项目文件名、贴图和物体名字都只能用这些字符。')
            return
        for char in treeName:
            if char not in (string.letters+string.digits+'_'):
                cmds.confirmDialog(message=u'命名只能由【英文】、【数字】和【下划】线构成，并且首字母必须是英文。\n请注意项目文件名、贴图和物体名字都只能用这些字符。\n\n发现资产名中输入了不识别的字：" %s "'%char.replace(' ',u'空格').replace('\t',u'ＴＡＢ'))
                return
        if treeName[0] not in string.letters:
            cmds.confirmDialog(message=u'命名只能由【英文】、【数字】和【下划】线构成，并且首字母必须是英文。\n请注意项目文件名、贴图和物体名字都只能用这些字符。\n\n发现资产名不符合规范')
            return
        if typeOMI in [1,2,3,4]:
            #~ if cmds.objExists('*_model_group') == True:
                #~ cmds.select('*_model_group')
                #~ GRPName = cmds.ls(sl = True)
            GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
            if GRPName!=[]:
                if cmds.objExists(GRPName[0] + '.treeName') == True:
                    treeType = cmds.getAttr(GRPName[0] + '.Type')
                    if (typeOMI==1 and treeType =='c') or (typeOMI==2 and treeType =='p') or (typeOMI==3 and treeType =='s'):
                        if self.renameTree_1() == 'OK':
                            if treeName.strip() == '':
                                cmds.confirmDialog(message = u'请输入名字', button = ['Yes'], defaultButton = 'Yes')
                            else:
                                cmds.delete(GRPName[0])
                                self.charactersTree()                        
                    else:
                        NameStr = cmds.getAttr(GRPName[0] + '.treeName')
                        confirmD = cmds.confirmDialog(message = u'已有组:' + NameStr + u'   是否清除原有组(包括组里物体)创建新组？', button = ['Yes', 'No'], defaultButton = 'Yes')
                else:
                    cmds.addAttr(GRPName[0], longName = 'treeName', dataType = 'string')
                    cmds.setAttr(GRPName[0] + '.treeName', treeName, type = 'string', lock = True)
                if confirmD == 'Yes':
                    cmds.delete(GRPName)
                    if typeOMI == 1:
                        self.charactersTree()
                    if typeOMI == 2:
                        self.propsTree()
                    if typeOMI == 3:
                        self.sceneTree()
            else:
                if treeName.strip() == '':
                    cmds.confirmDialog(message = u'请输入名字', button = ['Yes'], defaultButton = 'Yes')
                else:
                    if typeOMI == 1:
                        self.charactersTree()
                    if typeOMI == 2:
                        self.propsTree()
                    if typeOMI == 3:
                        self.sceneTree()
                    if typeOMI == 4:
                        self.meshGenTree()
    def snakeCommand(self, button):
        buttonL = cmds.button(button, query = True, label = True)
        self.parentGrp(buttonL)
    def lashCommand_L(self):
        groupName = cmds.textField(self.textFG, query = True, text = True)
        Groups = '' + groupName +'_l_lash_group'
        objectName = cmds.ls(selection = True)
        if cmds.listRelatives(objectName,c=1,shapes=1) == None:
            cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes')
            return
        NewName = '' + groupName + '_l_lash'
        for i in objectName:
            cmds.select(i)
            if cmds.listRelatives(i,p=1)!= None and cmds.listRelatives(i,p=1)[0] == Groups:
                pass
            else:
                cmds.parent(i,Groups)
                cmds.rename(cmds.ls(sl=1),NewName)
                sel = cmds.ls(sl= True)[0]                         
                shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                cmds.rename(shape,self.getShapeName(sel))                
        cmds.inViewMessage(amg = '已入组', pos = 'midCenter', fade = True)
        cmds.select(cl=1)
    def lashCommand_R(self):
        groupName = cmds.textField(self.textFG, query = True, text = True)
        Groups = '' + groupName +'_r_lash_group'
        objectName = cmds.ls(selection = True)
        if cmds.listRelatives(objectName,c=1,shapes=1) == None:
            cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes')
            return
        NewName = '' + groupName + '_r_lash'
        for i in objectName:
            cmds.select(i)
            if cmds.listRelatives(i,p=1)!= None and cmds.listRelatives(i,p=1)[0] == Groups:
                pass
            else:            
                cmds.parent(i,Groups)
                cmds.rename(cmds.ls(sl=1),NewName)  
                sel = cmds.ls(sl= True)[0]                         
                shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                cmds.rename(shape,self.getShapeName(sel))                
        cmds.inViewMessage(amg = '已入组', pos = 'midCenter', fade = True)  
        cmds.select(cl=1)
    def charactersTree(self):
        FileType = ''
        treeName = cmds.textField(self.textFG, query = True, text = True).strip()
        modelGRP = FileType + treeName + '_model_group'
        geometryGRP = FileType + treeName + '_geometry_group'
        headGRP = FileType + treeName + '_head_group'
        hairGRP = FileType + treeName + '_hair_group'
        headassGRP = FileType + treeName + '_headass_group'
        
        tarGRP = FileType + treeName + '_tar_group'
        closeeyeGRP = FileType + treeName + '_closeeye_group'
        openeyeGRP = FileType + treeName + '_openeye_group'
        
        eyeGRP = FileType + treeName + '_eye_group'
        LeyeGRP = FileType + treeName + '_l_eye_group'
        ReyeGRP = FileType + treeName + '_r_eye_group'
        browGRP = FileType + treeName + '_brow_group'
        LbrowGRP = FileType + treeName + '_l_brow_group'
        RbrowGRP = FileType + treeName + '_r_brow_group'        
        lashGRP = FileType + treeName + '_lash_group'
        LlashGRP = FileType + treeName + '_l_lash_group'
        RlashGRP = FileType + treeName + '_r_lash_group'        
        earGRP = FileType + treeName + '_ear_group'
        LearGRP = FileType + treeName + '_l_ear_group'
        RearGRP = FileType + treeName + '_r_ear_group'
        beardGRP = FileType + treeName + '_beard_group'
        mouthGRP = FileType + treeName + '_mouth_group'
        tongueGRP = FileType + treeName + '_tongue_group'
        upteethGRP = FileType + treeName + '_upteeth_group'
        lowteethGRP = FileType + treeName + '_lowteeth_group'
        nonnasalityGRP = FileType + treeName + '_nonnasality_group'
        bodyGRP = FileType + treeName + '_body_group'
        bodyassGRP = FileType + treeName + '_bodyass_group'
        
        RarmGrp = FileType + treeName + '_r_arm_group'
        LarmGrp = FileType + treeName + '_l_arm_group'
        RhandGrp = FileType + treeName + '_r_hand_group'
        LhandGrp = FileType + treeName + '_l_hand_group'
        RlegGrp = FileType + treeName + '_r_leg_group'
        LlegGrp = FileType + treeName + '_l_leg_group'
        RshoeGrp = FileType + treeName + '_r_shoe_group'
        LshoeGrp =FileType + treeName + '_l_shoe_group'
        RfootGrp = FileType + treeName + '_r_foot_group'
        LfootGrp = FileType + treeName + '_l_foot_group'
        
        clothGRP = FileType + treeName + '_cloth_group'
        previewGRP = FileType + treeName + '_preview_group'
        deformGRP = FileType + treeName + '_deform_group'
        solverGRP = FileType + treeName + '_solver_group'
        #xxxGRP = FileType + treeName + '_xxx_group'
        nrigidGRP = FileType + treeName + '_nrigid_group'
        nclothGRP = FileType + treeName + '_ncloth_group'
        nucleusGRP = FileType + treeName + '_nucleus_group'
        cothfieldGRP = FileType + treeName + '_cothfield_group'
        solvermodelGRP = FileType + treeName + '_solvermodel_group'
        colliderGRP = FileType + treeName + '_collider_group'
        if cmds.objExists(modelGRP) == False:
            cmds.group(empty = True, name = modelGRP)
            cmds.addAttr(longName = 'treeName', dataType = 'string')
            cmds.addAttr(longName = 'Name',dataType = 'string')
            cmds.addAttr(longName = 'Type',dataType = 'string')
            cmds.setAttr(modelGRP + '.treeName', treeName, type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Name', 'model', type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Type', 'c', type = 'string', lock = True)
        if cmds.objExists(geometryGRP) == False:
            cmds.group(empty = True, name = geometryGRP, parent = modelGRP)
            self.addTreeAttr(geometryGRP,'geometrty')
            cmds.addAttr(geometryGRP,longName = 'Morh',dataType = 'string')
            cmds.setAttr(geometryGRP + '.Morh', 'm', type = 'string', lock = True) 
            cmds.addAttr(geometryGRP,longName = "rendering",at = 'bool')
            cmds.setAttr("%s.rendering"%geometryGRP, True)        
        if cmds.objExists(headGRP) == False:
            cmds.group(empty = True, name = headGRP, parent = geometryGRP)
            self.addTreeAttr(headGRP,'head')
        if cmds.objExists(hairGRP) == False:
            cmds.group(empty = True, name = hairGRP, parent = headGRP)
            self.addTreeAttr(hairGRP,'hair')
        if cmds.objExists(browGRP) == False:
            cmds.group(empty = True, name = browGRP, parent = headGRP)
            self.addTreeAttr(browGRP,'brow')
        if cmds.objExists(LbrowGRP) == False:
            cmds.group(empty = True, name = LbrowGRP, parent = browGRP)
            self.addTreeAttr(LbrowGRP,'Lbrow')
        if cmds.objExists(RbrowGRP) == False:
            cmds.group(empty = True, name = RbrowGRP, parent = browGRP) 
            self.addTreeAttr(RbrowGRP,'Rbrow')                   
        if cmds.objExists(lashGRP) == False:
            cmds.group(empty = True, name = lashGRP, parent = headGRP)
            self.addTreeAttr(lashGRP,'lash')
        if cmds.objExists(LlashGRP) == False:
            cmds.group(empty = True, name = LlashGRP, parent = lashGRP)
            self.addTreeAttr(LlashGRP,'Llash')
        if cmds.objExists(RlashGRP) == False:
            cmds.group(empty = True, name = RlashGRP, parent = lashGRP) 
            self.addTreeAttr(RlashGRP,'Rlash') 
        if cmds.objExists(eyeGRP) == False:
            cmds.group(empty = True, name = eyeGRP, parent = headGRP)
            self.addTreeAttr(eyeGRP,'eye')
        if cmds.objExists(LeyeGRP) == False:
            cmds.group(empty = True, name = LeyeGRP, parent = eyeGRP)
            self.addTreeAttr(LeyeGRP,'Leye')
        if cmds.objExists(ReyeGRP) == False:
            cmds.group(empty = True, name = ReyeGRP, parent = eyeGRP)
            self.addTreeAttr(ReyeGRP,'Reye')
        if cmds.objExists(earGRP) == False:
            cmds.group(empty = True, name = earGRP, parent = headGRP)
            self.addTreeAttr(earGRP,'ear')
        if cmds.objExists(LearGRP) == False:
            cmds.group(empty = True, name = LearGRP, parent = earGRP)
            self.addTreeAttr(LearGRP,'Lear')            
        if cmds.objExists(RearGRP) == False:
            cmds.group(empty = True, name = RearGRP, parent = earGRP) 
            self.addTreeAttr(RearGRP,'Rear')                           
        if cmds.objExists(mouthGRP) == False:
            cmds.group(empty = True, name = mouthGRP, parent = headGRP)
            self.addTreeAttr(mouthGRP,'mouth')
        if cmds.objExists(tongueGRP) == False:
            cmds.group(empty = True, name = tongueGRP, parent = mouthGRP)
            self.addTreeAttr(tongueGRP,'tongue')
        if cmds.objExists(upteethGRP) == False:
            cmds.group(empty = True, name = upteethGRP, parent = mouthGRP)
            self.addTreeAttr(upteethGRP,'upteeth')
        if cmds.objExists(lowteethGRP) == False:
            cmds.group(empty = True, name = lowteethGRP, parent = mouthGRP)
            self.addTreeAttr(lowteethGRP,'lowteeth')
        if cmds.objExists(nonnasalityGRP) == False:
            cmds.group(empty = True, name = nonnasalityGRP, parent = mouthGRP)
            self.addTreeAttr(nonnasalityGRP,'nonnasality')
        if cmds.objExists(beardGRP) == False:
            cmds.group(empty = True, name = beardGRP, parent = headGRP)
            self.addTreeAttr(beardGRP,'beard')
        if cmds.objExists(headassGRP) == False:
            cmds.group(empty = True, name = headassGRP, parent = headGRP)
            self.addTreeAttr(headassGRP,'headass')
        if cmds.objExists(tarGRP) == False:
            cmds.group(empty = True, name = tarGRP, parent = headGRP)
            self.addTreeAttr(tarGRP,'tar')            
        if cmds.objExists(closeeyeGRP) == False:
            cmds.group(empty = True, name = closeeyeGRP, parent = tarGRP)
            self.addTreeAttr(closeeyeGRP,'closeeye')                
        if cmds.objExists(openeyeGRP) == False:
            cmds.group(empty = True, name = openeyeGRP, parent = tarGRP)
            self.addTreeAttr(openeyeGRP,'openeye') 
            
            
        if cmds.objExists(bodyGRP) == False:
            cmds.group(empty = True, name = bodyGRP, parent = geometryGRP)
            self.addTreeAttr(bodyGRP,'body')
        if cmds.objExists(bodyassGRP) == False:
            cmds.group(empty = True, name = bodyassGRP, parent = bodyGRP)
            self.addTreeAttr(bodyassGRP,'bodyass')
        
            
            
        if cmds.objExists(RarmGrp) == False:
            cmds.group(empty = True, name = RarmGrp, parent = bodyGRP)            
            self.addTreeAttr(RarmGrp,'Rarm')
        if cmds.objExists(LarmGrp) == False:
            cmds.group(empty = True, name = LarmGrp, parent = bodyGRP)            
            self.addTreeAttr(LarmGrp,'Larm')
        if cmds.objExists(RhandGrp) == False:
            cmds.group(empty = True, name = RhandGrp, parent = bodyGRP)            
            self.addTreeAttr(RhandGrp,'Rhand')
        if cmds.objExists(LhandGrp) == False:
            cmds.group(empty = True, name = LhandGrp, parent = bodyGRP)            
            self.addTreeAttr(LhandGrp,'Lhand')
        if cmds.objExists(RlegGrp) == False:
            cmds.group(empty = True, name = RlegGrp, parent = bodyGRP)            
            self.addTreeAttr(RlegGrp,'Rleg')            
        if cmds.objExists(LlegGrp) == False:
            cmds.group(empty = True, name = LlegGrp, parent = bodyGRP)            
            self.addTreeAttr(LlegGrp,'Lleg') 
        if cmds.objExists(RshoeGrp) == False:
            cmds.group(empty = True, name = RshoeGrp, parent = bodyGRP)            
            self.addTreeAttr(RshoeGrp,'Rshoe') 
        if cmds.objExists(LshoeGrp) == False:
            cmds.group(empty = True, name = LshoeGrp, parent = bodyGRP)            
            self.addTreeAttr(LshoeGrp,'Lshoe') 
        if cmds.objExists(RfootGrp) == False:
            cmds.group(empty = True, name = RfootGrp, parent = bodyGRP)            
            self.addTreeAttr(RfootGrp,'Rfoot') 
        if cmds.objExists(LfootGrp) == False:
            cmds.group(empty = True, name = LfootGrp, parent = bodyGRP)            
            self.addTreeAttr(LfootGrp,'Lfoot')             
            
        if cmds.objExists(clothGRP) == False:
            cmds.group(empty = True, name = clothGRP, parent = geometryGRP)
            self.addTreeAttr(clothGRP,'cloth')

        
        if cmds.objExists(previewGRP) == False:
            cmds.group(empty = True, name = previewGRP, parent = geometryGRP)
            self.addTreeAttr(previewGRP,'preview')
            cmds.addAttr(previewGRP,longName = "preview",at = 'bool')
            cmds.setAttr("%s.preview"%previewGRP, True)  




        if cmds.objExists(deformGRP) == False:
            cmds.group(empty = True, name = deformGRP, parent = modelGRP)
            self.addTreeAttr(deformGRP,'deform')
        if cmds.objExists(solverGRP) == False:
            cmds.group(empty = True, name = solverGRP, parent = modelGRP)
            self.addTreeAttr(solverGRP,'solver')
        if cmds.objExists(cothfieldGRP) == False:
            cmds.group(empty = True, name = cothfieldGRP, parent = solverGRP)
            self.addTreeAttr(cothfieldGRP,'cothfield')
        if cmds.objExists(solvermodelGRP) == False:
            cmds.group(empty = True, name = solvermodelGRP, parent = solverGRP)
            self.addTreeAttr(solvermodelGRP,'solvermodel')
        cmds.select(clear = True)
    def hairTree(self):
        FileType = ''
        treeName = cmds.textField(self.textFG, query = True, text = True).strip()
        modelGRP = FileType + treeName + '_model_group'
        geometryGRP = FileType + treeName + '_geometry_group'                  
        solverHairGRP = FileType + treeName + '_solverHair_group'
        hairYetiGRP = FileType + treeName + '_hairYeti_group'
        hairCollideGRP = FileType + treeName + '_hairCollide_group'
        hairsysGRP = FileType + treeName + '_hairsys_group'
        hairxxxGRP = FileType + treeName + '_xxx_nhair_group'
        hairsysNodeGRP = FileType + treeName + '_hairsysNode_group'
        follicGRP = FileType + treeName + '_follic_group'
        pfxhairGRP = FileType + treeName + '_pfxhair_group'
        outputcurvesGRP = FileType + treeName + '_outputcurves_group'
        HairnodesGRP = FileType + treeName + '_Hairnodes_group'
        HairfieldGRP = FileType + treeName + '_Hairfield_group'
        growMeshGRP = FileType + treeName + '_growMesh_group'

        if cmds.objExists(modelGRP) == False:
            cmds.group(empty = True, name = modelGRP)
            cmds.addAttr(longName = 'treeName', dataType = 'string')
            cmds.addAttr(longName = 'Name',dataType = 'string')
            cmds.addAttr(longName = 'Type',dataType = 'string')
            cmds.setAttr(modelGRP + '.treeName', treeName, type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Name', 'model', type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Type', 'c', type = 'string', lock = True)
        if cmds.objExists(geometryGRP) == False:
            cmds.group(empty = True, name = geometryGRP, parent = modelGRP)
            self.addTreeAttr(geometryGRP,'geometrty')            
            cmds.addAttr(geometryGRP,longName = 'Morh',dataType = 'string')
            cmds.setAttr(geometryGRP + '.Morh', 'h', type = 'string', lock = True)                    
        if cmds.objExists(solverHairGRP) == False:
            cmds.group(empty = True, name = solverHairGRP, parent = geometryGRP)
            self.addTreeAttr(solverHairGRP,'solverHair')
        if cmds.objExists(hairYetiGRP) == False:
            cmds.group(empty = True, name = hairYetiGRP, parent = solverHairGRP)
            self.addTreeAttr(hairYetiGRP,'hairYeti')
        if cmds.objExists(hairCollideGRP) == False:
            cmds.group(empty = True, name = hairCollideGRP, parent = solverHairGRP)
            self.addTreeAttr(hairCollideGRP,'hairCollide')
        if cmds.objExists(hairsysGRP) == False:
            cmds.group(empty = True, name = hairsysGRP, parent = solverHairGRP) 
            self.addTreeAttr(hairsysGRP,'hairsys')       
        if cmds.objExists(hairxxxGRP) == False:
            cmds.group(empty = True, name = hairxxxGRP, parent = hairsysGRP) 
            self.addTreeAttr(hairxxxGRP,'hairxxx')          
        if cmds.objExists(hairsysNodeGRP) == False:
            cmds.group(empty = True, name = hairsysNodeGRP, parent = hairxxxGRP)    
            self.addTreeAttr(hairsysNodeGRP,'hairsysNode')        
        if cmds.objExists(follicGRP) == False:
            cmds.group(empty = True, name = follicGRP, parent = hairxxxGRP)
            self.addTreeAttr(follicGRP,'follic')
        if cmds.objExists(pfxhairGRP) == False:
            cmds.group(empty = True, name = pfxhairGRP, parent = hairxxxGRP)
            self.addTreeAttr(pfxhairGRP,'pfxhair')
        if cmds.objExists(outputcurvesGRP) == False:
            cmds.group(empty = True, name = outputcurvesGRP, parent = hairxxxGRP)
            self.addTreeAttr(outputcurvesGRP,'outputcurves')
        if cmds.objExists(HairnodesGRP) == False:
            cmds.group(empty = True, name = HairnodesGRP, parent = solverHairGRP)
            self.addTreeAttr(HairnodesGRP,'Hairnodes')
        if cmds.objExists(HairfieldGRP) == False:
            cmds.group(empty = True, name = HairfieldGRP, parent = solverHairGRP)
            self.addTreeAttr(HairfieldGRP,'Hairfield')
        if cmds.objExists(growMeshGRP) == False:
            cmds.group(empty = True, name = growMeshGRP, parent = solverHairGRP)  
            self.addTreeAttr(growMeshGRP,'growMesh')              
        cmds.select(clear = True)        
        
        
        
    def propsTree(self):
        FileType = ''
        treeName = cmds.textField(self.textFG, query = True, text = True).strip()
        modelGRP = FileType + treeName + '_model_group'
        geometryGRP = FileType + treeName + '_geometry_group'
        previewGRP = FileType + treeName + '_preview_group' 
        if cmds.objExists(modelGRP) == False:
            cmds.group(empty = True, name = modelGRP)
            cmds.addAttr(longName = 'treeName', dataType = 'string')
            cmds.addAttr(longName = 'Name',dataType = 'string')
            cmds.addAttr(longName = 'Type',dataType = 'string')
            cmds.setAttr(modelGRP + '.treeName', treeName, type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Name', 'model', type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Type', 'p', type = 'string', lock = True)            
        if cmds.objExists(geometryGRP) == False:
            cmds.group(empty = True, name = geometryGRP, parent = modelGRP)
            cmds.addAttr(geometryGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(geometryGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(geometryGRP + '.Name', 'geometry', type = 'string', lock = True)
            cmds.setAttr(geometryGRP + '.Type', 'p', type = 'string', lock = True)
            cmds.addAttr(geometryGRP,longName = "rendering",at = 'bool')
            cmds.setAttr("%s.rendering"%geometryGRP, True)           
        if cmds.objExists(previewGRP) == False:
            cmds.group(empty = True, name = previewGRP, parent = geometryGRP)
            cmds.addAttr(previewGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(previewGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(previewGRP + '.Name', 'preview', type = 'string', lock = True)
            cmds.setAttr(previewGRP + '.Type', 'p', type = 'string', lock = True)
            cmds.addAttr(previewGRP,longName = "preview",at = 'bool')
            cmds.setAttr("%s.preview"%previewGRP, True)     
        
        
        cmds.select(clear = True)
    def sceneTree(self):
        FileType = ''
        treeName = cmds.textField(self.textFG, query = True, text = True).strip()
        modelGRP = FileType + treeName + '_model_group'
        geometryGRP = FileType + treeName + '_geometry_group'
        previewGRP = FileType + treeName + '_preview_group' 
        if cmds.objExists(modelGRP) == False:
            cmds.group(empty = True, name = modelGRP)
            cmds.addAttr(longName = 'treeName', dataType = 'string')
            cmds.addAttr(longName = 'Name',dataType = 'string')
            cmds.addAttr(longName = 'Type',dataType = 'string')
            cmds.setAttr(modelGRP + '.treeName', treeName, type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Name', 'model', type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Type', 's', type = 'string', lock = True)    
        if cmds.objExists(geometryGRP) == False:
            cmds.group(empty = True, name = geometryGRP, parent = modelGRP)
            cmds.addAttr(geometryGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(geometryGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(geometryGRP + '.Name', 'geometry', type = 'string', lock = True)
            cmds.setAttr(geometryGRP + '.Type', 's', type = 'string', lock = True)   
            cmds.addAttr(geometryGRP,longName = "rendering",at = 'bool')
            cmds.setAttr("%s.rendering"%geometryGRP, True)      
        if cmds.objExists(previewGRP) == False:
            cmds.group(empty = True, name = previewGRP, parent = geometryGRP)
            cmds.addAttr(previewGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(previewGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(previewGRP + '.Name', 'preview', type = 'string', lock = True)
            cmds.setAttr(previewGRP + '.Type', 'p', type = 'string', lock = True)
            cmds.addAttr(previewGRP,longName = "preview",at = 'bool')
            cmds.setAttr("%s.preview"%previewGRP, True) 
        
        
        cmds.select(clear = True)
    def meshGenTree(self):
        FileType = ''
        treeName = cmds.textField(self.textFG, query = True, text = True).strip()
        modelGRP = FileType + treeName + '_model_group'
        geometryGRP = FileType + treeName + '_geometry_group'
        previewGRP = FileType + treeName + '_preview_group'
        if cmds.objExists(modelGRP) == False:
            cmds.group(empty = True, name = modelGRP)
            cmds.addAttr(longName = 'treeName', dataType = 'string')
            cmds.addAttr(longName = 'Name',dataType = 'string')
            cmds.addAttr(longName = 'Type',dataType = 'string')
            cmds.setAttr(modelGRP + '.treeName', treeName, type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Name', 'model', type = 'string', lock = True)
            cmds.setAttr(modelGRP + '.Type', 'm', type = 'string', lock = True)    
        if cmds.objExists(geometryGRP) == False:
            cmds.group(empty = True, name = geometryGRP, parent = modelGRP)
            cmds.addAttr(geometryGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(geometryGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(geometryGRP + '.Name', 'geometry', type = 'string', lock = True)
            cmds.setAttr(geometryGRP + '.Type', 'm', type = 'string', lock = True)  
            cmds.addAttr(geometryGRP,longName = "rendering",at = 'bool')
            cmds.setAttr("%s.rendering"%geometryGRP, True)       
        if cmds.objExists(previewGRP) == False:
            cmds.group(empty = True, name = previewGRP, parent = geometryGRP)
            cmds.addAttr(previewGRP,longName = 'Name',dataType = 'string')
            cmds.addAttr(previewGRP,longName = 'Type',dataType = 'string')
            cmds.setAttr(previewGRP + '.Name', 'preview', type = 'string', lock = True)
            cmds.setAttr(previewGRP + '.Type', 'p', type = 'string', lock = True)
            cmds.addAttr(previewGRP,longName = "preview",at = 'bool')
            cmds.setAttr("%s.preview"%previewGRP, True)  
        cmds.select(clear = True)
        pass
    def GRPExists(self):
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        #~ if cmds.objExists('*_model_group') == True:
            #~ cmds.select('*_model_group')
            #~ GRPName = cmds.ls(sl = True)
        if GRPName !=[]:
            treeName = '_'.join(GRPName[0].split('_')[1:GRPName[0].split('_').index('model')])
            if GRPName[0][0:1] == 'c':
                
                cmds.optionMenu(self.typeOM, edit = True, select = 1)      
                self.characterComp()
            if GRPName[0][0:1] == 'p':
                cmds.optionMenu(self.typeOM, edit = True, select = 2)
                self.propComp()    
            if GRPName[0][0:1] == 's':
                cmds.optionMenu(self.typeOM, edit = True, select = 3)
                self.propComp()  
            if cmds.objExists(GRPName[0] + '.treeName') == True:
                self.GRPName = GRPName
                self.getGRPName()
            else:
                cmds.addAttr(GRPName[0], longName = 'Name', dataType = 'string')
                cmds.setAttr(GRPName[0] + '.treeName', treeName[1], type = 'string', lock = True)
                self.GRPName = GRPName
                self.getGRPName()
    def getGRPName(self):
        creatTWindow = self.creatTWindow
        GRPName = self.GRPName
        NameStr = cmds.getAttr(GRPName[0] + '.treeName')
        treeName = '_'.join(GRPName[0].split('_')[1:GRPName[0].split('_').index('model')])
        Type = cmds.getAttr(GRPName[0] + '.Type')
        cmds.select(clear = True)
        if cmds.objExists(''+treeName+'_geometry_group') and cmds.getAttr(''+treeName+'_geometry_group.Morh') == 'm':
            cmds.window(creatTWindow, title = u'已有人物组:' + NameStr, edit = True)
            cmds.textField(self.textFG, edit = True, text = NameStr)
            cmds.frameLayout(self.controlFrL, edit = True, collapse = False)  
            cmds.optionMenu(self.typeOM, edit = True, select = 1)  
        if cmds.objExists(''+treeName+'_geometry_group') and cmds.getAttr(''+treeName+'_geometry_group.Morh') == 'h':
            cmds.window(creatTWindow, title =  u'已有毛发组:' + NameStr, edit = True)
            cmds.textField(self.textFG, edit = True, text = NameStr)
            cmds.frameLayout(self.controlFrL, edit = True, collapse = False)  
            cmds.optionMenu(self.typeOM, edit = True, select = 1)          
        if Type == 'p':
            cmds.window(creatTWindow, title = u'已有道具组:' + NameStr, edit = True)
            cmds.textField(self.textFG, edit = True, text = NameStr)            
        if Type == 's':
            cmds.window(creatTWindow, title = u'已有场景组:' + NameStr, edit = True)
            cmds.textField(self.textFG, edit = True, text = NameStr)                     
    def multipleGRP(self):
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        #~ if cmds.objExists('*_model_group') == True:
            #~ cmds.select('*_model_group')
            #~ GRPName = cmds.ls(selection = True)
        if GRPName !=[]:
            GRPNum = len(GRPName)
            GRPList = []
            if GRPNum > 1:
                for i in GRPName:
                    GRPList.append(i)
                holdGrp = cmds.confirmDialog(message = u'请选择一个组保留', button = GRPList)
                cmds.select(GRPName)
                cmds.select(holdGrp, deselect = True)
                deleteList = cmds.ls(selection = True)
                cmds.delete(deleteList)
    def confirmDA(self):
        cmds.confirmDialog(message = u'请创建组', button = ['Yes'], defaultButton = 'Yes')
    def parentGrp(self, buttonName):
        #~ if cmds.objExists('*_model_group') == True:
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        if GRPName !=[]:
            groupName = cmds.textField(self.textFG, query = True, text = True)
            objectName = cmds.ls(selection = True)
            self.objectName = objectName
            parentName = ''
            typeOMI = cmds.optionMenu(self.typeOM, query = True, select = True)
            if typeOMI == 1: # or typeOMI == 4:
                parentName = '' + groupName + '_' + buttonName + '_group'
                self.parentName = parentName
                if cmds.objExists(parentName) == True:
                    if objectName != []:
                        self.parentGrpB()
                    else:
                        cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes') 
                else :
                    cmds.confirmDialog(message = u'该组不存在，请手动检查组', button = ['Yes'], defaultButton = 'Yes')                                
            if typeOMI == 2:
                parentName = '' + groupName + '_' + buttonName + '_group'
                self.parentName = parentName
                if cmds.objExists(parentName) == True:
                    if objectName != []:
                        self.parentGrpA()
                    else:
                        cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes')   
                else:
                    cmds.confirmDialog(message = u'请先创建道具组', button = ['Yes'], defaultButton = 'Yes')   
                                                 
            if typeOMI == 3:
                parentName = '' + groupName + '_' + buttonName + '_group'
                self.parentName = parentName
                if cmds.objExists(parentName) == True:
                    if objectName != []:
                        self.parentGrpA()
                    else:
                        cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes')
                else:
                    cmds.confirmDialog(message = u'请先创建场景组', button = ['Yes'], defaultButton = 'Yes') 
            if typeOMI == 4:
                parentName = '' + groupName + '_' + buttonName + '_group'
                self.parentName = parentName
                if cmds.objExists(parentName) == True:
                    if objectName != []:
                        self.parentGrpA()
                    else:
                        cmds.confirmDialog(message = u'请选择物体', button = ['Yes'], defaultButton = 'Yes')
                else:
                    cmds.confirmDialog(message = u'请先创建场景组', button = ['Yes'], defaultButton = 'Yes') 

        else:
            self.confirmDA()       
    def parentGrpA(self):
        groupName = cmds.textField(self.textFG, query = True, text = True)
        typeOMI = cmds.optionMenu(self.typeOM, query = True, select = True)
        objectName = self.objectName
        parentName = self.parentName
        if cmds.listRelatives(objectName,c=1,shapes=1) == None:
            cmds.confirmDialog(message=u'请先选择物体')
            return
        self.textnameDialog=''
        self.nameDialog()
        if self.textnameDialog=='':
            return
        if typeOMI == 2:
            newGroupName = '' + groupName + '_' + self.textnameDialog + '_group'
            newObjName = '' + groupName + '_' + self.textnameDialog + '_1'
            if cmds.objExists(newGroupName):
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True)[0]
                    if cmds.listRelatives(sel,p=1):
                        if cmds.listRelatives(sel,p=1)[0] != newGroupName:
                            cmds.parent(sel, newGroupName)
                    if  cmds.listRelatives(sel,p=1) == None :
                        cmds.parent(sel, newGroupName)
                    sel = cmds.ls(sl= True)[0]
                    cmds.rename(sel, newObjName) 
                    sel = cmds.ls(sl= True)[0]                         
                    shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                    cmds.rename(shape,self.getShapeName(sel))                   
                    cmds.select(cl=1)
            else :
                cmds.select(cl=1)
                cmds.group(name = newGroupName,em=1,parent = parentName)
                cmds.addAttr(newGroupName,longName = 'Name',dataType = 'string')
                cmds.addAttr(newGroupName,longName = 'Type',dataType = 'string')
                cmds.setAttr(newGroupName + '.Name', self.textnameDialog , type = 'string', lock = True)
                cmds.setAttr(newGroupName + '.Type', 'p', type = 'string', lock = True) 
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True)[0]

                    try:   
                        cmds.parent(sel, newGroupName)
                        sel = cmds.ls(sl= True)[0]
                        cmds.rename(sel, newObjName) 
                        sel = cmds.ls(sl= True)[0]                         
                        shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                        cmds.rename(shape,self.getShapeName(sel))                    
                        cmds.select(cl=1)
                    except:
                        print 'no grouped'           
            cmds.optionVar(iv = ['inViewMessageEnable', 1])
            cmds.inViewMessage(amg = u'已入组', pos = 'midCenter', fade = True)
            cmds.select(clear = True)            
        if typeOMI == 3:
            newGroupName = '' + groupName + '_' + self.textnameDialog+'_group'
            newObjName ='' + groupName + '_' + self.textnameDialog +'_1'
            if cmds.objExists(newGroupName):
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True)
                    if cmds.listRelatives(sel,p=1):
                        if cmds.listRelatives(sel,p=1)[0] != newGroupName:
                            cmds.parent(sel, newGroupName)
                    if  cmds.listRelatives(sel,p=1) == None :
                        cmds.parent(sel, newGroupName)
                    cmds.rename(sel, newObjName)   
                    cmds.select(cl=1)
            else :
                cmds.select(cl=1)
                cmds.group(name = newGroupName,em=1,parent = parentName)
                cmds.addAttr(newGroupName,longName = 'Name',dataType = 'string')
                cmds.addAttr(newGroupName,longName = 'Type',dataType = 'string')
                cmds.setAttr(newGroupName + '.Name', self.textnameDialog , type = 'string', lock = True)
                cmds.setAttr(newGroupName + '.Type', 's', type = 'string', lock = True) 
                cmds.select(cl=1)
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True,long=1)
                    try:
                        cmds.parent(sel, newGroupName)
                        sel = cmds.ls(sl = True,long=1)
                        cmds.rename(sel[0], newObjName) 
                        cmds.select(cl=1) 
                    except:
                        print 'no grouped'
            cmds.optionVar(iv = ['inViewMessageEnable', 1])
            cmds.inViewMessage(amg = u'已入组', pos = 'midCenter', fade = True)
            cmds.select(clear = True)      
        if typeOMI == 4:
            newGroupName = '' + groupName + '_' + self.textnameDialog+'_group'
            newObjName ='' + groupName + '_' + self.textnameDialog +'_1'
            if cmds.objExists(newGroupName):
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True)
                    if cmds.listRelatives(sel,p=1):
                        if cmds.listRelatives(sel,p=1)[0] != newGroupName:
                            cmds.parent(sel, newGroupName)
                    if  cmds.listRelatives(sel,p=1) == None :
                        cmds.parent(sel, newGroupName)
                    cmds.rename(sel, newObjName)   
                    cmds.select(cl=1)
            else :
                cmds.select(cl=1)
                cmds.group(name = newGroupName,em=1,parent = parentName)
                cmds.addAttr(newGroupName,longName = 'Name',dataType = 'string')
                cmds.addAttr(newGroupName,longName = 'Type',dataType = 'string')
                cmds.setAttr(newGroupName + '.Name', self.textnameDialog , type = 'string', lock = True)
                cmds.setAttr(newGroupName + '.Type', 'm', type = 'string', lock = True) 
                cmds.select(cl=1)
                for obj in objectName:
                    cmds.select(obj)
                    sel = cmds.ls(sl = True,long=1)
                    try:
                        cmds.parent(sel, newGroupName)
                        sel = cmds.ls(sl = True,long=1)
                        cmds.rename(sel[0], newObjName) 
                        cmds.select(cl=1) 
                    except:
                        print 'no grouped'
            cmds.optionVar(iv = ['inViewMessageEnable', 1])
            cmds.inViewMessage(amg = u'已入组', pos = 'midCenter', fade = True)
            cmds.select(clear = True)      
    def parentGrpB(self):
        objectName = self.objectName
        if cmds.listRelatives(objectName,c=1,shapes=1) == None:
            cmds.confirmDialog(message=u'请先选择物体')
            return
        parentName = self.parentName
        typeOMI = cmds.optionMenu(self.typeOM, query = True, select = True)

        objectNewName = parentName.split('_group')[0]
        parentList = cmds.listRelatives(parentName, children = True)
        if parentList == None:
            for i in objectName:
                cmds.select(i)
                sel = cmds.ls(sl= True)[0]
                cmds.parent(sel, parentName)
                sel = cmds.ls(sl= True)[0]
                cmds.rename(sel, objectNewName)
                sel = cmds.ls(sl= True)[0]                         
                shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                cmds.rename(shape,self.getShapeName(sel))                
                cmds.optionVar(iv = ['inViewMessageEnable', 1])
                cmds.inViewMessage(amg = u'已入组', pos = 'midCenter', fade = True)
                cmds.select(clear = True)
        else:
            for i in objectName:
                if i in parentList:
                    cmds.optionVar(iv = ['inViewMessageEnable', 1])
                    cmds.inViewMessage(amg = u'已存在', pos = 'midCenter', fade = True)
                    cmds.select(clear = True)
                else:
                    cmds.select(i)
                    sel = cmds.ls(sl= True)[0]
                    if cmds.listRelatives(sel,p=1)!= None:
                        if cmds.listRelatives(sel,p=1)[0]== parentName:
                            pass
                        else :
                            cmds.parent(sel, parentName)
                    else :
                        cmds.parent(sel, parentName)
                    sel = cmds.ls(sl= True)[0]
                    cmds.rename(sel, objectNewName)       
                    sel = cmds.ls(sl= True)[0]                         
                    shape = cmds.listRelatives(sel,shapes=1,f=1)[0]
                    cmds.rename(shape,self.getShapeName(sel))
                    cmds.optionVar(iv = ['inViewMessageEnable', 1])
                    cmds.inViewMessage(amg = u'已入组', pos = 'midCenter', fade = True)
                    cmds.select(clear = True)                    
    def nameDialog(self):
        result = cmds.promptDialog(title='Rename Object',message='Enter Name:',button=['OK', 'Cancel'],defaultButton='OK',cancelButton='Cancel')
        if result == 'OK' :
            if cmds.promptDialog(query=True, text=True) !='':
                self.textnameDialog = cmds.promptDialog(query=True, text=True)
                return
            else:
                self.nameDialog()
        else:
            self.textnameDialog = ''
            return
    def judgeWin(self):
        if cmds.optionMenu(self.typeOM,q=1,sl=1) == 1 :
            cmds.deleteUI(self.controlFrL)  
            self.characterComp()
        if cmds.optionMenu(self.typeOM,q=1,sl=1) == 2 :
            cmds.deleteUI(self.controlFrL)
            self.propComp()  
        if cmds.optionMenu(self.typeOM,q=1,sl=1) == 3 :
            cmds.deleteUI(self.controlFrL)
            self.propComp()                
        if cmds.optionMenu(self.typeOM,q=1,sl=1) == 4 :
            cmds.deleteUI(self.controlFrL)
            self.propComp()                
    def addTreeAttr(self,groupName,attrName):
        cmds.addAttr(groupName,longName = 'Name',dataType = 'string')
        cmds.addAttr(groupName,longName = 'Type',dataType = 'string')
        cmds.setAttr(groupName + '.Name', attrName, type = 'string', lock = True)
        cmds.setAttr(groupName + '.Type', 'c', type = 'string', lock = True)        
    
    def renameTree_1(self):
        treeName = cmds.textField(self.textFG, query = True, text = True)
        NameStr = ''
        TypeStr = ''
        TreeName = ''
        #~ if cmds.objExists('*_model_group') == True:
            #~ cmds.select('*_model_group')
            #~ GRPName = cmds.ls(sl = True)
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        if GRPName!=[]:
            if cmds.objExists(GRPName[0] + '.treeName') == True:
                NameStr = cmds.getAttr(GRPName[0] + '.treeName')   
                TypeStr = cmds.getAttr(GRPName[0] + '.Type')
                TreeName = cmds.getAttr(GRPName[0] + '.treeName')     
        trans = list(set(cmds.ls(tr=1)) - set([u'front',u'persp',u'side',u'top']))  

        if cmds.optionMenu(self.typeOM,q=1,sl=1) == 1 :
            if cmds.objExists(''+TreeName+'_geometry_group.Morh') and cmds.getAttr(''+TreeName+'_geometry_group.Morh') == 'm':
                for i in trans:
                    newName = treeName + NameStr.join(i.split(NameStr)[1:])
                    if cmds.objExists(i+'.treeName'):
                        cmds.setAttr(i+'.treeName',l=0)
                        cmds.setAttr(i+'.treeName',treeName,type = 'string')
                        cmds.setAttr(i+'.treeName',l=1)
                    cmds.rename(i,newName)   
            else :
                con = cmds.confirmDialog(message=u'大纲中的大组不是人物组，请问要删除当前组(包括组里的物体)并且新建人物组吗?',button=['OK', 'Cancel'],defaultButton='OK',cancelButton='Cancel')
                return con
        else:
            for i in trans:
                newName = treeName + NameStr.join(i.split(NameStr)[1:])
                if cmds.objExists(i+'.treeName'):
                    cmds.setAttr(i+'.treeName',l=0)
                    cmds.setAttr(i+'.treeName',treeName,type = 'string')
                    cmds.setAttr(i+'.treeName',l=1)
                cmds.rename(i,newName)
    
    def renameTree_2(self):
        treeName = cmds.textField(self.textFG, query = True, text = True)
        NameStr = ''
        TypeStr = ''
        TreeName = ''
        #~ if cmds.objExists('*_model_group') == True:
            #~ cmds.select('*_model_group')
            #~ GRPName = cmds.ls(sl = True)
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        if GRPName!=[]:
            if cmds.objExists(GRPName[0] + '.treeName') == True:
                NameStr = cmds.getAttr(GRPName[0] + '.treeName')   
                TypeStr = cmds.getAttr(GRPName[0] + '.Type')
                TreeName = cmds.getAttr(GRPName[0] + '.treeName')     
        trans = list(set(cmds.ls(tr=1)) - set([u'front',u'persp',u'side',u'top']))
        if cmds.objExists(''+TreeName+'_geometry_group.Morh') and cmds.getAttr(''+TreeName+'_geometry_group.Morh') == 'h':
            for i in trans:
                newName = treeName + NameStr.join(i.split(NameStr)[1:])
                if cmds.objExists(i+'.treeName'):
                    cmds.setAttr(i+'.treeName',l=0)
                    cmds.setAttr(i+'.treeName',treeName,type = 'string')
                    cmds.setAttr(i+'.treeName',l=1)
                cmds.rename(i,newName)   
        else :
            con = cmds.confirmDialog(message=u'大纲中的大组不是头发组，请问要删除当前组(包括组里的物体)并新建头发组吗?',button=['OK', 'Cancel'],defaultButton='OK',cancelButton='Cancel')
            return con                    
    def setDisplay(self):
         #~ if cmds.objExists('*_model_group') == True :
             #~ groups = cmds.ls('*_model_group')[0]
        GRPName = [x for x in cmds.ls(type='transform') if ('_model_group' in x) ]
        if GRPName!=[]:
            groups = GRPName[0]
            attr = 1-cmds.getAttr(groups+'.v')
            cmds.setAttr((groups + '.v'),attr)
    # def getShapeName(self,transName):
    #     #     if transName[-1] in string.digits:
    #     #         return transName[:-1] + 'Shape' + transName[-1]
    #     #     else :
    #     #         return transName + 'Shape'
#修复shape命名错误的bug
    def getShapeName(self, transName):
        if transName.replace("_", "").isalnum() is True:#判断去掉_以后是否为纯字母，目的是判断有数字
            temp_num = []
            stop = -1
            for i in range(-1, -10, -1):#判断后10位，一直到出现字母
                if transName[i].isdigit():
                    temp_num.append(transName[i])#如果是数字就一直加下去，直到遇见字母或者是到10位数以后
                else:
                    stop = i
                    break
            temp_num.reverse()#序列倒序
            return transName[:stop] + 'Shape' + "{}".format("".join(temp_num))#重命名
        else:
            return transName + 'Shape'#如果为纯字母的话就直接改名字

    def colliderApp(self):
        colliderGroup.ColliderGroup().showUi()
    def setNameSpace(self):
        cmds.namespace(setNamespace = ':')
if __name__ == '__main__':
    ModelArrange = Ui()
    ModelArrange.showUi()