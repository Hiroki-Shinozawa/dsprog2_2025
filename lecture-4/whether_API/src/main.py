import flet as ft
import requests
import json

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT

    # 地域リストを取得
    def get_areas():
        try:
            response = requests.get("http://www.jma.go.jp/bosai/common/const/area.json")
            data = response.json()
            return data
        except Exception as e:
            print(f"Error fetching areas: {e}")
            return None

    # 天気予報を取得
    def get_forecast(code):
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
            response = requests.get(url)
            data = response.json()
            return data
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None

    areas_data = get_areas()
    if not areas_data:
        page.add(ft.Text("地域データの取得に失敗しました。"))
        return

    centers = areas_data.get("centers", {})
    offices = areas_data.get("offices", {})

    # 地方選択ドロップダウン
    center_dropdown = ft.Dropdown(
        label="地方を選択",
        options=[ft.dropdown.Option(key=k, text=v["name"]) for k, v in centers.items()],
        on_change=lambda e: update_offices(e.control.value)
    )

    # 地域選択ドロップダウン
    office_dropdown = ft.Dropdown(
        label="地域を選択",
        disabled=True
    )

    # 天気情報表示
    weather_text = ft.Text("", size=16)

    def update_offices(center_code):
        if center_code:
            center_info = centers[center_code]
            office_codes = center_info.get("children", [])
            office_options = []
            for code in office_codes:
                if code in offices:
                    office_options.append(ft.dropdown.Option(key=code, text=offices[code]["name"]))
            office_dropdown.options = office_options
            office_dropdown.disabled = False
            office_dropdown.value = None
            weather_text.value = ""
        else:
            office_dropdown.options = []
            office_dropdown.disabled = True
            office_dropdown.value = None
            weather_text.value = ""
        page.update()

    def fetch_weather(e):
        code = office_dropdown.value
        if code:
            forecast_data = get_forecast(code)
            if forecast_data:
                # 最初のタイムシリーズの最初のエリアの天気
                time_series = forecast_data[0]["timeSeries"][0]
                areas = time_series["areas"]
                if areas:
                    area = areas[0]
                    weather = area.get("weathers", [""])[0]
                    weather_text.value = f"天気: {weather}"
                else:
                    weather_text.value = "天気情報が見つかりません。"
            else:
                weather_text.value = "天気情報の取得に失敗しました。"
        else:
            weather_text.value = "地域を選択してください。"
        page.update()

    # ボタン
    fetch_button = ft.ElevatedButton("天気を取得", on_click=fetch_weather)

    page.add(
        ft.Column([
            center_dropdown,
            office_dropdown,
            fetch_button,
            weather_text
        ])
    )

ft.app(target=main)
