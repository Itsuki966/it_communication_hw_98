import json
import pprint

# kyokustarとkyokuendの取得のための関数
def kyokustart_kyokuend(paifu):
    kyokustart = []
    kyokuend = []

    for i in range(len(paifu)):
        c = paifu[i]["cmd"]
        if c == 'kyokustart':
            kyokustart.append(i)
        elif c == 'kyokuend':
            kyokuend.append(i)
    
    return kyokustart, kyokuend



# ゲームスタートまでの準備ようの関数(配牌とゲーム状況を保存する辞書を作成)
def game_ready (paifu, kyoku):

  tehai = {}
  alldict = {}
  naki_dict = {}

  for i in range(kyokustart[kyoku], kyokuend[kyoku]+1):
    cmd = paifu[i]['cmd']

    # 親を保存
    if cmd == "dice":
      first_player = paifu[i+2]['args'][0]

    # 配牌
    elif cmd == "haipai":
      player = paifu[i]['args'][0]
      if player not in tehai:
        tehai[player] = [paifu[i]['args'][1][l] + paifu[i]['args'][1][l+1] for l in range(0,len(paifu[i]['args'][1])-1,2)]
        naki_dict[player] = 0
      else:
        if len(paifu[i]['args'][1]) != 2:
          for l in range(0, len(paifu[i]['args'][1])-1,2):
            pai = paifu[i]['args'][1][l] + paifu[i]['args'][1][l+1]
            tehai[player].append(pai)
        else:
          tehai[player].append(paifu[i]['args'][1])


  # 全てを保存する辞書の作成
  alldict['tehai'] = tehai[first_player]
  alldict['tsumo'] = [0]
  alldict['tedashi'] = [0]
  alldict['tsumogiri'] = [0]
  alldict['dora'] = [0,0,0,0]


  # 各プレイヤーごとに捨て牌のリストを作成し、辞書に追加
  key = list(tehai.keys())
  for k in key:
    alldict[k] = {"sutehai":[0*s for s in range(1,26)],"naki":[[0*i for i in range(1,5)],[0*i for i in range(1,5)],[0*i for i in range(1,5)],[0*i for i in range(1,5)]], "richi":[0]}

  return tehai, alldict, naki_dict


# ツモしてから牌を切るまでの関数
def do_sutehai(player,tsumo, sutehai, alldict, record, n):
  alldict['tsumo'][0] = tsumo
  alldict['tedashi'][0] = sutehai
  del alldict[player]['sutehai'][0]
  print("プレイヤー：", player)
  print(alldict)
  print("")
  # record.append(alldict)
  record[n] = alldict
  alldict[player]['sutehai'].append(sutehai)
  
 
# 鳴いた時の処理を行う関数     
def do_pon_chi(n, paifu, player, naki_dict, tehai, alldict, record):
  naki = paifu[n-1]['args'][1]
  naki_sutehai = paifu[n+2]['args'][1]
  open_pai = paifu[n+1]['args'][1].replace("<","").replace(">","")
  alldict['tehai'] = tehai[player]
  
  alldict[player]['naki'][naki_dict[player]] = [open_pai[l] + open_pai[l+1] for l in range(0,len(open_pai)-1,2)]
  alldict[player]['naki'][naki_dict[player]].append(naki)
  alldict[player]['naki'][naki_dict[player]].append(0)
  do_sutehai(player, naki, naki_sutehai, alldict, record, n)
  
  tehai[player].append(naki)
  tehai[player].remove(naki_sutehai)
  
  for s in range(len(alldict[player]['naki'][naki_dict[player]])-1):
    tehai[player].remove(alldict[player]['naki'][naki_dict[player]][s])
    tehai[player].append(0)
  
  naki_dict[player] += 1  
  

# ゲーム進行中の処理用の関数
def game(paifu, tehai, alldict, kyoku, naki_dict):
  dora_count = 0
  # record = []
  record = {}

  for n in range(kyokustart[kyoku], kyokuend[kyoku]+1):
    cmd = paifu[n]['cmd']
    alldict['tsumogiri'] = 0
    
    # ツモから牌を切るまで
    if cmd == "tsumo":
      player = paifu[n]['args'][0]
      tsumo = paifu[n]['args'][2]
      alldict['tehai'] = tehai[player]
      if paifu[n+1]['cmd'] == 'sutehai':
        sutehai = paifu[n+1]['args'][1]
        
        # ツモギリだった場合フラグを立てる
        if sutehai == tsumo:
          alldict['tsumogiri'] = 1
          
        do_sutehai(player, tsumo, sutehai, alldict, record,n)
        tehai[player].append(tsumo)
        tehai[player].remove(sutehai)
      elif paifu[n+1]['args'][1] == 'richi':
        sutehai = paifu[n+2]['args'][1]
        do_sutehai(player, tsumo, sutehai, alldict, record, n)
        tehai[player].append(tsumo)
        tehai[player].remove(sutehai)
      elif paifu[n+1]['args'][1] == 'tsumo' or paifu[n+1]['args'][1] == 'ron':
        alldict['tsumo'][0] = tsumo
        alldict['tedashi'][0] = sutehai
        alldict[player]['sutehai'].append(sutehai)
        del alldict[player]['sutehai'][0]
      else:
        sutehai = 0
      
    # ドラを保存
    elif cmd == "dora":
      dora = paifu[n]['args'][0]
      alldict['dora'][dora_count] = dora
      dora_count += 1
      
    elif cmd == "agari":
      pass
      print(paifu[n]['args'])
      print("----------------------------------------------------------------------")

    elif cmd == "ryukyoku":
      pass
      print("流局")
      print("----------------------------------------------------------------------")

    # 鳴き
    elif cmd == "say":
    #   鳴きの種類を取得
      say = paifu[n]['args'][1]
      player = paifu[n]['args'][0]

      if say == 'pon':
        print(f'#ポン：{player}')
        do_pon_chi(n, paifu, player, naki_dict, tehai, alldict, record)

      elif say == 'chi':
        print(f"#チー：{player}")
        do_pon_chi(n, paifu, player, naki_dict, tehai, alldict, record)
        

      elif say == 'kan':
        kan = paifu[n-1]['args'][2]

        tehai[player].append(kan)

        naki_list = alldict[player]['naki'][naki_dict[player]]
        
        if kan[0] == "5":
          for M in range(0,3):
            naki_list[M] = kan.lower()
          naki_list[3] = kan.upper()
          
          for kd in range(0,4):
            tehai[player].remove(naki_list[kd])
            tehai[player].append(0)
            
        else:
          for m in range(0,4):
            naki_list[m] = kan
            tehai[player].remove(kan)
            tehai[player].append(0)
        
        tehai[player].remove(0)    
        naki_dict[player] += 1
        alldict['tsumo'][0] = kan
        print("カンしたよ")
        print("プレイヤー：", player)
        print(alldict)
        print("")
        record[n] = alldict
        

      elif say == 'richi':
        alldict[player]['richi'][0] = 1
        print("リーチしたよ")
        print("プレイヤー：", player)
        print(alldict)
        print("")
        record[n] = alldict
        
  return record
        
 
# jsonファイルの読み込み
paifu_path = str(input("表示する牌譜のファイルパスを入力してください。"))
with open(paifu_path) as f:
  paifu_data = json.load(f)        

kyokustart, kyokuend = kyokustart_kyokuend(paifu_data)

print(f"{len(kyokustart)}局まであります。")
kyoku = int(input("表示する局を入力してください"))

tehai, alldict, naki_dict = game_ready(paifu_data, kyoku-1)
record = game(paifu_data, tehai, alldict, kyoku-1, naki_dict)

record_path = '/Users/itsukikuwahara/Documents/class/it_tue/records/' + paifu_path[61:].replace(".json", "") + "_" + str(kyoku) + ".json"

with open(record_path, 'w') as w:
  json.dump(record, w)