from Web import create_app

# Создаём приложение
app = create_app()

# Запускаем приложение
if __name__ == "__main__":
    app.run(debug=True)