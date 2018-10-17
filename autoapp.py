from charge.app import create_app

app = create_app(cli=True)
app.run()
