from django.shortcuts import render, redirect
import requests
#import country_converter as coco  # 国名をISOコードに変換するためのライブラリ
import matplotlib.pyplot as plt
import io
import base64
from io import BytesIO
from matplotlib import font_manager
import csv
import pandas as pd
from django.http import HttpResponse
#from io import StringIO
from django.contrib import messages
import urllib.parse

# 日本語の国名とISO3コードのマッピング
country_to_iso3 = {
    "アフガニスタン": "AFG",
    "アルバニア": "ALB",
    "アルジェリア": "DZA",
    "アメリカ合衆国": "USA",
    "アメリカ": "USA",
    "アルゼンチン": "ARG",
    "オーストラリア": "AUS",
    "オーストリア": "AUT",
    "バングラデシュ": "BGD",
    "ベルギー": "BEL",
    "ブラジル": "BRA",
    "カナダ": "CAN",
    "チリ": "CHL",
    "中国": "CHN",
    "コロンビア": "COL",
    "チェコ": "CZE",
    "エジプト": "EGY",
    "フランス": "FRA",
    "ドイツ": "DEU",
    "インド": "IND",
    "インドネシア": "IDN",
    "イラン": "IRN",
    "イラク": "IRQ",
    "イスラエル": "ISR",
    "イタリア": "ITA",
    "ジャマイカ": "JAM",
    "日本": "JPN",
    "ヨルダン": "JOR",
    "カザフスタン": "KAZ",
    "ケニア": "KEN",
    "韓国": "KOR",
    "クウェート": "KWT",
    "ラトビア": "LVA",
    "レバノン": "LBN",
    "リビア": "LBY",
    "リトアニア": "LTU",
    "ルクセンブルク": "LUX",
    "メキシコ": "MEX",
    "モロッコ": "MAR",
    "モザンビーク": "MOZ",
    "オランダ": "NLD",
    "ニュージーランド": "NZL",
    "ノルウェー": "NOR",
    "パキスタン": "PAK",
    "パナマ": "PAN",
    "ペルー": "PER",
    "フィリピン": "PHL",
    "ポーランド": "POL",
    "ポルトガル": "PRT",
    "カタール": "QAT",
    "ルーマニア": "ROU",
    "ロシア": "RUS",
    "サウジアラビア": "SAU",
    "シンガポール": "SGP",
    "南アフリカ": "ZAF",
    "南アフリカ共和国": "ZAF",
    "スペイン": "ESP",
    "スリランカ": "LKA",
    "スウェーデン": "SWE",
    "スイス": "CHE",
    "シリア": "SYR",
    "台湾": "TWN",
    "タンザニア": "TZA",
    "タイ": "THA",
    "トルコ": "TUR",
    "ウガンダ": "UGA",
    "ウクライナ": "UKR",
    "アラブ首長国連邦": "ARE",
    "イギリス": "GBR",
    "ウルグアイ": "URY",
    "ベネズエラ": "VEN",
    "ベトナム": "VNM",
    "イエメン": "YEM",
    "ジンバブエ": "ZWE"
}

"""
    日本語の国名をISO3コードに変換
    country_nameがリストにない場合は、エラーメッセージを返す
    """
def get_iso3_from_japanese_country_name(country_name):
    if country_name in country_to_iso3:
        return country_to_iso3[country_name]
    else:
        return "Invalid country name"    # 無効な国名の場合にエラーメッセージを返す

def user_input_view(request):
    """
    ユーザー入力フォームを表示
    """
    return render(request, 'weatherco2app/user_input_form.html')

# Windows環境で一般的な日本語フォント（MS Gothic）を指定
#font_path = 'C:\\Windows\\Fonts\\msgothic.ttc'    #Windows環境のみ Renderではエラー  
#prop = font_manager.FontProperties(fname=font_path)

# 日本語表示の設定
#plt.rcParams['font.family'] = prop.get_name()    Renderでエラーとなったため、削除 Windowsフォントのため、Linux環境のRenderでエラー
# 代わりに、以下のようなコードを使用
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']

def submit_data(request):
    if request.method == "POST":
        # ユーザー入力を取得
        country = request.POST.get("country", "").strip()
        start_year = request.POST.get("start_year", "").strip()
        end_year = request.POST.get("end_year", "").strip()

        # 数字に変換
        try:
            start_year = int(start_year)
            end_year = int(end_year)
        except ValueError:
            # 数字以外が入力された場合のエラーハンドリング
            return render(request, 'weatherco2app/result.html', {"error": "無効な年が選択されました。"})
        
        # 開始年より終了年が前の場合にエラー
        if end_year < start_year:
            return render(request, 'weatherco2app/result.html', {"error": "終了年は開始年以降の年を選択してください。"})

        # 日本語の国名をISO3コードに変換
        country_code = get_iso3_from_japanese_country_name(country)

        if country_code == "Invalid country name":
            # 国名が無効な場合、エラーメッセージを表示
            error_message = f"{country}は有効な国名ではありません。正しい国名を入力してください。"
            return render(request, 'weatherco2app/error.html', {"error": error_message})

        # World Bank APIからデータ取得
        try:
            co2_data = []
            for year in range(int(start_year), int(end_year) + 1):
                api_url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/EN.GHG.CO2.MT.CE.AR5?date={year}&format=json"
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()

                # APIのレスポンスを確認
                print(f"API Response for {country} ({year}): {data}")

                if data and len(data) > 1 and data[1]:
                    co2_value = data[1][0].get('value', None)
                    if co2_value is not None:
                        co2_data.append({"year": year, "co2_emission": co2_value})
                    else:
                        co2_data.append({"year": year, "co2_emission": "No data"})
                else:
                    co2_data.append({"year": year, "co2_emission": "No data"})
        except requests.exceptions.RequestException as e:
            co2_data = {"error": f"Failed to fetch data from World Bank API: {e}"}

        # グラフの生成
        graph_data = None
        if co2_data and isinstance(co2_data, list):
            years = [item['year'] for item in co2_data]
            emissions = [item['co2_emission'] if isinstance(item['co2_emission'], (int, float)) else 0 for item in co2_data]

            # 日本語の国名をタイトルに表示
            country_name_for_title = country  

            plt.figure(figsize=(8, 5))
            plt.bar(years, emissions)
            plt.title(f"CO₂ Emissions for {country_name_for_title} from {start_year} to {end_year}")
            plt.xlabel("Year")
            plt.ylabel("CO₂ Emissions (MtCO₂e)")
            plt.tight_layout()

            # 画像をBase64にエンコード
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graph_data = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()

        context = {
            'country': country,
            'start_year': start_year,
            'end_year': end_year,
            'co2_data': co2_data,
            'graph_data': graph_data,  # Base64エンコードされた画像データ
        }

        # 結果をセッションに保存
        request.session['co2_data'] = co2_data
        request.session['country'] = country
        request.session['start_year'] = start_year
        request.session['end_year'] = end_year
        request.session['graph_data'] = graph_data

        return render(request, 'weatherco2app/result.html', context)

    elif request.method == "GET":
        # ダウンロードリクエストの処理
        if 'download' in request.GET:
            co2_data = request.session.get('co2_data')
            country = request.session.get('country')
            
            if not co2_data or not country:
                messages.error(request, "データが見つかりません。再度検索してください。")
                return redirect('weatherco2app:user_input')

            if request.GET['download'] == 'csv':
                return download_csv(co2_data, country)
            elif request.GET['download'] == 'excel':
                return download_excel(co2_data, country)

        # 通常のGETリクエスト（結果の表示）
        co2_data = request.session.get('co2_data')
        country = request.session.get('country')
        start_year = request.session.get('start_year')
        end_year = request.session.get('end_year')
        graph_data = request.session.get('graph_data')

        if not co2_data:
            return render(request, 'weatherco2app/user_input_form.html')

        context = {
            'country': country,
            'start_year': start_year,
            'end_year': end_year,
            'co2_data': co2_data,
            'graph_data': graph_data,
        }
        return render(request, 'weatherco2app/result.html', context)

    return render(request, 'weatherco2app/user_input_form.html')

def download_csv(co2_data, country):
    """
    CO2データをCSVとしてダウンロード
    """
    # レスポンスの設定
    response = HttpResponse(content_type='text/csv')
    safe_filename = urllib.parse.quote(f"{country}_co2_data.csv")
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{safe_filename}'

    # CSV書き込み
    writer = csv.writer(response)
    writer.writerow(['Year', 'CO2 Emission (MtCO2e)'])
    
    for item in co2_data:
        writer.writerow([item['year'], item['co2_emission']])

    return response

def download_excel(co2_data, country):
    """
    CO2データをExcelファイルとしてダウンロード
    """
    # pandasを使ってExcelファイルを生成
    df = pd.DataFrame(co2_data)

    # カラム名を変更して単位を追加
    df = df.rename(columns={'co2_emission': 'CO2 Emission (MtCO2e)'})

    # Excel出力
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    safe_filename = urllib.parse.quote(f"{country}_co2_data.xlsx")
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{safe_filename}'

    # Excelに書き込み
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CO2 Emissions')

    return response   

