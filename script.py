import os
import struct
from functions import *

def patch_blarc(aspect_ratio, folder):
    aspect_ratio = float(aspect_ratio)
    print(f"Aspect ratio is {aspect_ratio}")

    file_paths = {}


    layout_map = {
                    'EntMain': ['N_CntL', 'N_Lock', 'N_CntR', 'N_AlarmChildLock', 'L_AlarmHud', 'P_AlarmBase', 'L_AlarmPageIndicator', 'L_AlarmGoEnt', 'L_AlarmBtnPagerR', 'L_AlarmBtnPagerL', 'L_BtnBack', 'L_Lock', 'N_AlarmCtrlResume', 'N_AlarmCtrlCntHud', 'N_News', 'N_AlarmCtrlNtf'],
                    'RdtBase': ['N_ScrollArea', 'N_ScrollWindow', 'T_Blank', 'N_GameRoot', 'N_System', 'L_ChildLock', 'N_MyPage', 'L_Hud', 'L_BalloonCtrl', 
                                'L_BtnAccount_00', 'L_BtnAccount_01', 'L_BtnAccount_02', 'L_BtnAccount_03', 'L_BtnAccount_04', 'L_BtnAccount_05', 'L_BtnAccount_06', 'L_BtnAccount_07',
                                # 'N_Icon_00', 'N_Icon_01', 'N_Icon_02', 'N_Icon_03', 'N_Icon_04', 'N_Icon_05', 'N_Icon_06', 'N_Icon_07', 'N_Icon_08', 'N_Icon_09', 'N_Icon_10', 'N_Icon_11', 'N_Icon_12', 'L_BtnChangeUser', 'L_BtnFlc',
                                'L_BtnLR', 'L_BtnNoti', 'L_BtnShop', 'L_BtnPvr', 'L_BtnCtrl', 'L_BtnSet', 'L_BtnPow'],
                }

    def patch_ui_layouts(direction):
        if direction == "x":
            offset = 0x40
        if direction == 'y':
            offset = 0x48

        for filename, panes in layout_map.items():
            modified_name = filename + "_name"
            paths = file_paths.get(modified_name, [])
            
            if not paths:
                default_path = os.path.join(folder, "region_common", "ui", "GameMain", "blyt", f"{filename}.bflyt")
                paths.append(default_path)
            
            for full_path_of_file in paths:
                with open(full_path_of_file, 'rb') as f:
                    content = f.read().hex()
                
                start_rootpane = content.index(b'RootPane'.hex())
                
                for pane in panes:
                    pane_hex = pane.encode('utf-8').hex()
                    start_pane = content.index(pane_hex, start_rootpane)
                    idx = start_pane + offset 
                    
                    current_value_hex = content[idx:idx+8]
                    current_value = hex2float(current_value_hex)
                    
                    new_value = (current_value * s1**-1)
                    new_value_hex = float2hex(new_value)

                    if pane == "L_SetItem_00" or pane == "L_SetItem_01" or pane == "L_SetItem_02" :
                        print(pane, current_value, new_value)
                    
                    content = content[:idx] + new_value_hex + content[idx+8:]
                
                with open(full_path_of_file, 'wb') as f:
                    f.write(bytes.fromhex(content))

    def patch_blyt(filename, pane, operation, value):
        if operation in ["scale_x", "scale_y"]:
            if value < 1:
                command = "Squishing"
            elif value > 1:
                command = "Stretching"
            else:
                command = "Ignoring"
        elif operation in ["shift_x", "shift_y"]:
            command = "Shifting"
        
        print(f"{command} {pane} of {filename}")
        
        offset_dict = {'shift_x': 0x40, 'shift_y': 0x48, 'scale_x': 0x70, 'scale_y': 0x78}
        modified_name = filename + "_name"
        
        # Get all paths for the given filename
        paths = file_paths.get(modified_name, [])
        if not paths:
            # If no paths are found, create a default path and add it to the list
            default_path = os.path.join(folder, "Layout", f"{filename}.Nin_NX_NVN", "blyt", f"{filename}.bflyt")
            paths.append(default_path)
        
        for full_path_of_file in paths:
            with open(full_path_of_file, 'rb') as f:
                content = f.read().hex()
            
            start_rootpane = content.index(b'RootPane'.hex())
            pane_hex = str(pane).encode('utf-8').hex()
            start_pane = content.index(pane_hex, start_rootpane)
            idx = start_pane + offset_dict[operation]
            content_new = content[:idx] + float2hex(value) + content[idx+8:]
            
            with open(full_path_of_file, 'wb') as f:
                f.write(bytes.fromhex(content_new))


            
    blyt_folder = os.path.abspath(os.path.join(folder))
    file_names_stripped = []
    
    do_not_scale_rootpane = ["BaseBg", "BaseNml","RdtBg", "BaseTop", "BlurBg2", "BaseBlurBg2", "IconGame", "SystemAppletFader", "RdtBtnIconGame"]
   
    rootpane_by_y = []

    file_paths = {}
    file_names_stripped = []

    for root, dirs, files in os.walk(blyt_folder):
        for file_name in files:
            if file_name.endswith(".bflyt"):
                stripped_name = file_name.strip(".bflyt")
                file_names_stripped.append(stripped_name)
                full_path = os.path.join(root, file_name)
                modified_name = stripped_name + "_name"
                if modified_name not in file_paths:
                    file_paths[modified_name] = []
                file_paths[modified_name].append(full_path)

    
    if aspect_ratio >= 16/9:
        s1 = (16/9)  / aspect_ratio
        print(f"Scaling factor is set to {s1}")
        s2 = 1-s1
        s3 = s2/s1
        s4 = (16/10) / aspect_ratio
        
        for name in file_names_stripped:
            if name in do_not_scale_rootpane:
                    print(f"Skipping RootPane scaling of {name}")
            if name not in do_not_scale_rootpane:
                patch_blyt(name, 'RootPane', 'scale_x', s1)
            if name in rootpane_by_y:
                patch_blyt(name, 'RootPane', 'scale_y', 1/s1)
                patch_blyt(name, 'RootPane', 'scale_x', 1)

        patch_blyt("RdtBase", 'L_BgNml', 'scale_x', 1/s1)
        patch_ui_layouts('x')
        patch_blyt("RdtBase", 'N_GameRoot', 'shift_x', -200)
    
    else:
        s1 = aspect_ratio / (16/9)
        s2 = 1-s1
        s3 = s2/s1
        
        for name in file_names_stripped:
            if name in do_not_scale_rootpane:
                print(f"Skipping root pane scaling of {name}")
            if name not in do_not_scale_rootpane:
                print(f"Scaling root pane vertically for {name}")
                patch_blyt(name, 'RootPane', 'scale_y', s1)
