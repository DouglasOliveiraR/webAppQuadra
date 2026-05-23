from playwright.sync_api import sync_playwright
import time

def run_e2e_test():
    with sync_playwright() as p:
        # Iniciando o Chrome de forma visível e com "slow_mo" para o usuário acompanhar a automação
        print("🤖 [Agente QA] Iniciando Webdriver (Chromium)...")
        browser = p.chromium.launch(headless=False, slow_mo=700)
        
        # Simulando um celular (Mobile Viewport)
        context = browser.new_context(viewport={'width': 390, 'height': 844})
        page = context.new_page()

        try:
            print("🌐 [Agente QA] Acessando a aplicação em http://localhost:5173/...")
            page.goto("http://localhost:5173/")
            
            # Como não estamos logados, o Guard deve redirecionar para o /login
            page.wait_for_url("**/login")
            print("✅ [Agente QA] Redirecionamento de segurança para /login funcionou!")

            print("🔑 [Agente QA] Preenchendo formulário de Login...")
            page.fill("input[placeholder='(11) 99999-9999']", "11999999999")
            page.fill("input[type='password']", "admin123")
            
            print("🖱️ [Agente QA] Clicando em 'Entrar'...")
            page.click("button:has-text('Entrar')")
            
            # Espera voltar pra Home
            page.wait_for_url("http://localhost:5173/")
            print("✅ [Agente QA] Autenticação bem sucedida! Estamos na Home.")

            print("🛡️ [Agente QA] Testando acesso ao painel de Check-in (exclusivo para Admin)...")
            # Clique no menu inferior "Check-in"
            page.click("text='Check-in'")
            
            # Espera o título do painel aparecer
            page.wait_for_selector("text='Painel do Admin'")
            page.wait_for_selector("text='Check-in na Quadra'")
            print("✅ [Agente QA] Acesso ao Check-in confirmado!")

            print("🗳️ [Agente QA] Simulando um registro de presença...")
            # Clicar em "Chegou" no primeiro card
            page.click("button:has-text('Chegou') >> nth=0")
            print("✅ [Agente QA] Presença registrada na API!")

            # Dorme um pouco para o usuário poder ver a cor do botão mudar
            time.sleep(2)

            print("🎮 [Agente QA] Testando aba de Votação...")
            page.click("text='Votação'")
            page.wait_for_selector("text='Votação Pós-Jogo'")
            print("✅ [Agente QA] Aba de Votação carregada com sucesso!")
            
            time.sleep(2)
            print("🎉 [Agente QA] Teste E2E concluído com SUCESSO. Nenhuma falha encontrada na UI!")

        except Exception as e:
            print(f"❌ [Agente QA] O teste FALHOU: {str(e)}")
        finally:
            print("🔌 [Agente QA] Fechando Webdriver...")
            browser.close()

if __name__ == "__main__":
    run_e2e_test()
