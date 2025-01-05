import matplotlib
matplotlib.use('Agg')  # バックエンドをAggに設定
import matplotlib.pyplot as plt
import platform
import requests
import io
import base64
from io import BytesIO
from matplotlib import font_manager
import csv
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import urllib.parse
import os
import pycountry

def set_font():
    """
    フォント設定
    """
    try:
        # DejaVu Sansフォントを指定
        font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        print(f"Font set to: {font_prop.get_name()}")
    except Exception as e:
        print(f"Font setting failed: {e}")

    font_paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/app/.fonts/NotoSansCJK-Regular.ttc'  # Heroku環境用
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
            return
    
    # デフォルトフォント
    plt.rcParams['font.family'] = 'sans-serif'

    """
    フォント設定
    複数の環境に対応したフォント設定
    """
    font_paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/app/.fonts/NotoSansCJK-Regular.ttc'  # Heroku環境用
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
            return
    
    # デフォルトフォント
    plt.rcParams['font.family'] = 'sans-serif'

    
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

def get_iso3_from_japanese_country_name(country_name):
    if country_name in country_to_iso3:
        return country_to_iso3[country_name]
    else:
        return "Invalid country name"

def get_country_name_from_iso3(iso3_code):
    """
    ISO3コードから国名（英語）を取得
    """
    try:
        country = pycountry.countries.get(alpha_3=iso3_code)
        return country.name if country else "Unknown"
    except KeyError:
        return "Unknown"

# フォント設定を初期化時に実行
set_font()

def user_input_view(request):
    """
    ユーザー入力フォームを表示
    """
    return render(request, 'weatherco2app/user_input_form.html')

def get_country_name_from_iso3(iso3_code):
    """
    ISO3コードから国名（英語）を取得
    """
    try:
        country = pycountry.countries.get(alpha_3=iso3_code)
        return country.name if country else "Unknown"
    except KeyError:
        return "Unknown"

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

        # ISO3コードから英語の国名を取得
        english_country_name = get_country_name_from_iso3(country_code)

        # World Bank APIからデータ取得
        try:
            co2_data = []
            for year in range(int(start_year), int(end_year) + 1):
                api_url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/EN.GHG.CO2.MT.CE.AR5?date={year}&format=json"
                response = requests.get(api_url)
                response.raise_for_status()

                data = response.json()

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

        # グラフ生成
        graph_data = None
        if co2_data and isinstance(co2_data, list):
            years = [item['year'] for item in co2_data]
            emissions = [item['co2_emission'] if isinstance(item['co2_emission'], (int, float)) else 0 for item in co2_data]

            plt.figure(figsize=(8, 5))
            plt.bar(years, emissions)
            plt.title(f"CO₂ Emissions in {english_country_name} from {start_year} to {end_year}", fontname='DejaVu Sans')
            plt.xlabel("Year")
            plt.ylabel("CO₂ Emissions (MtCO2e)")
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
