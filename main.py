import gameInformation, resource, phira, taptap
import sys, os, time, io
import pandas as pd
from moviepy import AudioFileClip
from pathlib import Path
import webbrowser


config = {
    'avatar': True, 
    'chart': True, 
    'illustrationBlur': False, 
    'illustrationLowRes': False, 
    'illustration': True, 
    'music': True, 
    'UPDATE': {
        'main_story': 0, 
        'other_song': 0, 
        'side_story': 0, 
    }
}


def is_valid_apk_path(path):
    return os.path.exists(path) and os.path.isfile(path) and path[-3:] == 'apk'

def process_lines(lines, max_fields):
    """将每一行的元素个数调整到max_fields，不足的用空元素补足"""
    processed_lines = []
    for line in lines:
        fields = line.rstrip('\n').split('\t')
        # 如果字段不足，补充空值
        while len(fields) < max_fields:
            fields.append('')
        processed_lines.append('\t'.join(fields))
    
    return processed_lines

def create_table(root_dir):
    
    ## 处理曲目基础信息
    info_path =  root_dir  + '/info/info.tsv'
    
    with open(info_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    processed_lines = process_lines(lines, 9)
    
    temp_content = '\n'.join(processed_lines)
    df = pd.read_table(io.StringIO(temp_content), header=None)
    df1 = df.drop(df.columns[0], axis=1)
    df1.columns = ['曲名', '曲师', '曲绘画师', 'EZ谱师', 'HD谱师', 'IN谱师', 'AT谱师', 'Legacy谱师']
    # df1.to_excel(root_dir + '/info.xlsx', sheet_name='基本信息', index=False)


    ## 处理曲目难度信息
    difficulty_path = root_dir + '/info/difficulty.tsv'

    with open(difficulty_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = process_lines(lines, 5)

    temp_content = '\n'.join(processed_lines)
    df2 = pd.read_table(io.StringIO(temp_content), header=None)
    
    df2.columns = ['曲名', 'EZ定数', 'HD定数', 'IN定数', 'AT定数']
    df2 = df2.drop('曲名', axis=1)      # 不要忘了drop不改变本身，需要赋值
    df2.insert(loc=0, column='曲名', value=df1['曲名'])
    # df2.to_excel(root_dir + '/info.xlsx', sheet_name='曲目定数', index=False)


    ## 得到总表，按难度降序排序
    df3 = df1.copy()
    df3.insert(loc=4, column='EZ定数', value=df2['EZ定数'])
    df3.insert(loc=6, column='HD定数', value=df2['HD定数'])
    df3.insert(loc=8, column='IN定数', value=df2['IN定数'])
    df3.insert(loc=10, column='AT定数', value=df2['AT定数'])
    df3 = df3.sort_values(['AT定数', 'IN定数', 'HD定数', 'EZ定数'], ascending=False)        # 依旧需要重新赋值
    # df3.to_excel(root_dir + '/info.xlsx', sheet_name='总表（按难度降序）', index=False)

    ## 输出excel文件
    with pd.ExcelWriter(root_dir + '/info.xlsx', engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='基本信息', index=False)

        df2.to_excel(writer, sheet_name='曲目定数', index=False)
        df2 = df2.sort_values(['AT定数', 'IN定数', 'HD定数', 'EZ定数'], ascending=False)
        df2.to_excel(writer, sheet_name='曲目定数（按难度降序）', index=False)
        
        df3.to_excel(writer, sheet_name='总表（按难度降序）', index=False)


def convert_to_mp3(folder_path):
    path = Path(folder_path)
    for file in path.glob('*.ogg'):
        audio_clip = AudioFileClip(file)
        audio_clip.write_audiofile(str(file)[:-4] + '.mp3')

        os.remove(file)
        print(f'{file}已删除')



def main():
    print("这里是Phi解包工具！")
    if input('是否需要下载Phi安装包？需要打任意字符回车，不需要直接回车跳过') != '':
        webbrowser.open(taptap.taptap(165287))      # Phigros的编号
        print('已经打开下载页面，请在下载完成后继续')

    if len(sys.argv) == 1:
        path = input('请输入Phi安装包文件路径：')
        while not is_valid_apk_path(path):
            print('路径无效！')
            path = input('请输入Phi安装包文件路径：')
        
    else:
        path = sys.argv[1]
        if not is_valid_apk_path(path):
            print('给定的apk路径无效！')
            time.sleep(3)
            exit()
    

    print('准备开始提取操作，可能花费较长时间，请耐心等待...')
    time.sleep(3)
    
    print('\n\n开始提取曲目各种数据...')
    time.sleep(1)
    try:
        os.makedirs('info', exist_ok=True)
        gameInformation.run(path)

        create_table('.')
    except:
        print('提取信息时出错，请检查给定的apk是否正确！')
        time.sleep(5)
        exit()
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    create_table(root_dir)

    print('\n\n开始提取音频、曲绘、头像、谱面资源...')
    time.sleep(1)
    for name in ['avatar', 'chart', 'illustration', 'music']:
        if not os.path.isdir(name):
            os.mkdir(name)
    
    resource.run(path, config)

    print('\n\n开始制作提取谱...')
    time.sleep(1)
    phira.main()

    print('\n\n开始转换音乐格式为mp3...')
    time.sleep(1)
    convert_to_mp3('music')

    print('\n\n全部完成！\n\n')
    time.sleep(1)
    print('说明：info.xlsx为所有曲目信息；\n' \
    'illustration文件夹中为全部高清曲绘；\n' \
    'avatar文件夹中为全部头像；\n' \
    'chart文件夹中为全部谱面的源文件；\n' \
    'music文件夹中为全部曲目的mp3音频；\n' \
    'phira文件夹中为全部曲目所有难度的提取谱文件，可以导入phira。')
    input('按回车键退出...')
    exit()



if __name__ == "__main__":
    main()

    # root_dir = os.path.dirname(os.path.abspath(__file__))
    # create_table(root_dir)

    # convert_to_mp3('music')