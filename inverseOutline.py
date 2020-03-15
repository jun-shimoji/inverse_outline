# coding:utf-8
import sublime
import sublime_plugin
import re


class InverseOutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # ヘッダ用の配列を作成
        header  = []
        # データ用の辞書を作成
        data    = {}
        data["project"] = set()
        data["member"] = set()
        mainkey = ""
        present_indent_level = 1
        longest_indent_level = 1
        present_indent_num   = 0

        # getting copied area. This "sel_area" is array
        sel_area = self.view.sel()
        f1 = self.view.substr(sel_area[0]).split('\n')
        f2 = ''
        # ヘッダの抽出
        for row in f1:
            print('row: ', str(row))
            editRow = re.search('^ *\+', row)
            if(editRow):
                if(int(editRow.end()) > present_indent_num):
                    present_indent_num   = editRow.end() - 1
                    present_indent_level = present_indent_num / 4 + 1
                    this_row = re.sub('^\s{' + str(present_indent_num) + '}\+\s', '', row).rstrip('\n')
                    print(str(present_indent_level) + " column is " + this_row)
                    if(present_indent_level >= longest_indent_level):
                        longest_indent_level = present_indent_level
                    header.append(this_row)

        # ヘッダ行の作成
        for e in header:
            f2 += '|' + e
        # しきり行の作成
        f2 += '|\n|'
        for e in header:
            f2 += '-|'

        # 読み込んだ行のインデントレベル
        present_indent_level = 1
        # present_indent_levelの前に設定されたインデントレベル
        cursor_indent_level = 1
        # インデントの要素数(例えば空白が4個、等)
        present_indent_num  = 0
        # 編集対象行かどうかのフラグ
        editRowFlg = False

        # Data部分の処理
        for row in f1:
            # インデントレベルの確認
            editRow  = re.search('^ *\-', row)
            anySpace = re.search('^ *', row)
            if(editRow):
                editRowFlg = True
                present_indent_num   = editRow.end() - 1
                present_indent_level = present_indent_num / 4 + 1
                # インデントレベル1の処理
                if present_indent_level == 1:
                    this_row = re.sub('^\s{' + str(present_indent_num) + '}\-\s', '', row).rstrip('\n')
                    data["project"].add(this_row)
                    mainkey = this_row
                    data[mainkey] = []
                    f2 += ('\n|' + this_row)
                    cursor_indent_level  = present_indent_level + 1
                # インデントレベル2以降の処理
                else:
                    this_row = re.sub('^\s{' + str(present_indent_num) + '}\-\s', '', row).rstrip('\n')
                    if present_indent_level == cursor_indent_level:
                        f2 += '|' + this_row
                    else:
                        f2 += '\n'
                        for i in range(int(present_indent_level)):
                            f2 += '|'
                        f2 += this_row
                    data[mainkey].append(this_row)
                    data["member"].add(this_row)
                    # インデントレベルが最大値の場合は敷居線を入れる
                    if present_indent_level == longest_indent_level:
                        f2 += '|'
                    cursor_indent_level  = present_indent_level + 1
            # 行末に敷居線を入れるかどうか(以外とややこしい)
            elif((anySpace and editRowFlg) and (present_indent_level != longest_indent_level)):
                f2 += '|'
                editRowFlg = False

        f2 += '\n\n'

        # メンバー配列の初期化
        for m in data["member"]:
            data[m] = []
        print('data', data)

        for p in data["project"]:
            for m in data["member"]:
                if(m in data[p]):
                    print("member: " + m + " project: " + p)
                    data[m].append(p)

        # ##### コンバート表の作成 #######
        longest_indent_level = 1
        # 最大column数を検索
        for m in data["member"]:
            if (len(data[m]) >= longest_indent_level):
                longest_indent_level = len(data[m])

        # ヘッダ行の作成
        f2 += '|name|'
        for p in range(longest_indent_level):
            f2 += '|'

        # しきり行の作成
        f2 += '\n|'
        for p in range(longest_indent_level):
            f2 += '-|'
        f2 += '\n'

        # データの作成
        for m in data["member"]:
            f2 += '|' + m
            for prj in data[m]:
                f2 += '|' + str(prj)
            f2 += '|\n|WR|\n|\n'

        self.view.insert(edit, len(sel_area[0]), f2)
