# 🧪 GUIA COMPLETO DE TESTES - Bot Travessia dos Sonhos

## 📋 O QUE SÃO ESSES TESTES?

Testes automatizados são como um **checklist automático** que verifica se tudo no bot está funcionando corretamente. É tipo ter um QA (testador) robô que testa TUDO em segundos!

### Por que isso é importante?

✅ **Segurança:** Antes de fazer deploy, você sabe que nada quebrou
✅ **Velocidade:** Testa em 30 segundos o que levaria 30 minutos manualmente
✅ **Confiança:** Pode mudar código sem medo de quebrar funcionalidades
✅ **Documentação:** Os testes mostram como o bot DEVE funcionar

---

## 🚀 COMO RODAR OS TESTES (SUPER FÁCIL)

### Opção 1: Windows (Duplo clique)

1. **Duplo clique** em `rodar_testes.bat`
2. Aguarde terminar
3. Abra o arquivo `relatorio_testes.html` no navegador
4. Pronto! 🎉

### Opção 2: Linha de comando (Windows/Linux/Mac)

```bash
# Modo simples
python rodar_testes.py

# Com relatório HTML visual
python rodar_testes.py --html

# Com análise de cobertura (% de código testado)
python rodar_testes.py --cobertura

# Modo rápido (pula testes lentos)
python rodar_testes.py --rapido
```

---

## 📊 ENTENDENDO OS RESULTADOS

### Símbolos que você vai ver:

- **`.`** (ponto verde) = Teste passou ✅
- **`F`** (F vermelho) = Teste falhou ❌
- **`s`** (s amarelo) = Teste pulado ⚠️
- **`E`** (E vermelho) = Erro no teste 💥

### Exemplo de saída:

```
test_bot_fluxo.py::TestComandosEspeciais::test_detectar_comando_menu PASSED  [ 5%]
test_bot_fluxo.py::TestComandosEspeciais::test_detectar_comando_resumo PASSED [ 10%]
test_bot_fluxo.py::TestEstadoAguardandoNome::test_nome_valido PASSED        [ 15%]
...

========================= 25 passed, 1 skipped in 3.45s =========================
```

**Tradução:**
- **25 passed** = 25 testes passaram ✅
- **1 skipped** = 1 teste foi pulado (normal)
- **3.45s** = Levou 3.45 segundos

---

## 🧪 O QUE ESTÁ SENDO TESTADO?

### 1. Comandos Especiais (5 testes)

Testa se os comandos funcionam a qualquer momento:

- ✅ `menu`, `voltar`, `inicio` → Volta ao menu
- ✅ `resumo`, `status` → Mostra dados coletados
- ✅ `ajuda`, `help`, `?` → Mostra ajuda
- ✅ `contato`, `falar`, `atendimento` → Solicita atendimento

**Por que isso importa:** Cliente não fica "preso" no fluxo

---

### 2. Estado: Aguardando Nome (3 testes)

Testa se o bot aceita/rejeita nomes corretamente:

- ✅ Nome válido: "Rafael" → Aceita
- ✅ Nome composto: "Maria Silva" → Aceita
- ❌ Nome com números: "Rafael123" → Rejeita

**Por que isso importa:** Evita dados inválidos no sistema

---

### 3. Estado: Aguardando Email (2 testes)

Testa validação de email:

- ✅ Email válido: "rafael@email.com" → Aceita
- ❌ Email inválido: "emailinvalido" → Rejeita

**Por que isso importa:** Garante que você consegue enviar proposta por email

---

### 4. Menu Principal (4 testes)

Testa as 3 opções do menu + opção inválida:

- ✅ Opção 1 → Apresenta empresa
- ✅ Opção 2 → Vai para qualificação
- ✅ Opção 3 → Solicita atendimento urgente
- ❌ Opção 999 → Mensagem de erro amigável

**Por que isso importa:** Cliente sempre encontra o que procura

---

### 5. Pós-Apresentação da Empresa (2 testes)

Testa resposta para veterano vs primeira vez:

- ✅ Opção 1 (veterano) → Mensagem personalizada
- ✅ Opção 2 (primeira vez) → Mensagem personalizada

**Por que isso importa:** Personalização aumenta engajamento

---

### 6. Qualificação Inicial (1 teste - PULADO)

Testa extração de dados com IA:

- ⚠️ **PULADO** porque requer API OpenAI (custa dinheiro rodar em teste)

**Como testar manualmente:**
1. Mande: "somos 4, 5 mil cada, dezembro"
2. Veja se o bot extrai corretamente:
   - Pessoas: 4
   - Orçamento: R$ 5.000
   - Quando: Dezembro

---

### 7. Fluxo Completo E2E (3 testes)

Testa o fluxo de ponta a ponta como um cliente real:

**Teste 1: Fluxo Rápido**
```
Nome → Email → Menu → Opção 2 → Qualificação → Experiência
→ Quando/Tempo → Contato → Horário → ✅ Atendimento Solicitado
```

**Teste 2: Comando 'resumo' no meio**
- Cliente pede resumo
- Bot mostra dados coletados
- Cliente continua de onde parou

**Teste 3: Comando 'menu' no meio**
- Cliente pede menu
- Bot volta ao menu
- Cliente pode escolher outra opção

**Por que isso importa:** Garante que o cliente consegue completar o cadastro

---

### 8. Validações de Segurança (3 testes)

Testa casos extremos:

- ✅ Mensagem com 1000 caracteres → Não quebra
- ❌ Nome com caracteres especiais → Rejeita
- ✅ Email com espaços → Remove espaços e aceita

**Por que isso importa:** Evita bugs e tentativas de invasão

---

## 📈 INTERPRETANDO COBERTURA DE CÓDIGO

Quando você roda com `--cobertura`, o relatório mostra **quantos % do código estão testados**.

### Exemplo:

```
Name                Stmts   Miss  Cover
---------------------------------------
app.py              450     120   73%
config.py           80      10    88%
---------------------------------------
TOTAL               530     130   75%
```

**Tradução:**
- **app.py:** 73% do código tem testes (bom!)
- **config.py:** 88% do código tem testes (excelente!)
- **TOTAL:** 75% de cobertura geral

### Metas:
- 🟢 **>70%** = Ótimo! Código bem testado
- 🟡 **50-70%** = Bom, mas pode melhorar
- 🔴 **<50%** = Precisa de mais testes

---

## ❌ O QUE FAZER QUANDO UM TESTE FALHA?

### Passo 1: Veja qual teste falhou

```
FAILED test_bot_fluxo.py::TestEstadoAguardandoNome::test_nome_valido
```

**Tradução:** O teste de nome válido falhou

### Passo 2: Leia a mensagem de erro

```
AssertionError: assert 'aguardando_nome' == 'aguardando_email'
```

**Tradução:** Esperava estado "aguardando_email" mas ficou em "aguardando_nome"

### Passo 3: Abra o relatório HTML

O arquivo `relatorio_testes.html` mostra:
- ✅ Linha exata que falhou
- 📸 Stack trace completo
- 🔍 Valores das variáveis

### Passo 4: Corrija o código

Duas possibilidades:

1. **Bug no código:** Arrume o código do bot
2. **Bug no teste:** Arrume o teste

### Passo 5: Rode novamente

```bash
python rodar_testes.py
```

---

## 🎯 QUANDO RODAR OS TESTES?

### ✅ SEMPRE que você:

1. **Fizer uma mudança no código**
   - Antes de fazer commit
   - Antes de fazer deploy

2. **Adicionar nova funcionalidade**
   - Escreva o teste ANTES do código (TDD)
   - Rode os testes para ver falhar
   - Implemente a funcionalidade
   - Rode novamente para ver passar ✅

3. **Corrigir um bug**
   - Escreva um teste que reproduz o bug
   - Arrume o código
   - Teste passa = bug corrigido!

4. **Antes de dormir tranquilo** 😴
   - Rode os testes
   - Tudo verde = pode dormir em paz

---

## 🆕 COMO ADICIONAR NOVOS TESTES?

### Exemplo: Testar novo estado "perguntando_idade"

```python
class TestPerguntandoIdade:
    """Testa novo estado de idade"""

    def test_idade_valida(self):
        """Testa idade válida"""
        estado = {
            "estado": "perguntando_idade",
            "nome": "Rafael"
        }

        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "25",
            estado
        )

        assert novo_estado["idade"] == 25
        assert novo_estado["estado"] == "proximo_estado"

    def test_idade_menor_18_rejeitada(self):
        """Testa que menor de 18 é rejeitado"""
        estado = {
            "estado": "perguntando_idade",
            "nome": "Rafael"
        }

        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "15",
            estado
        )

        # Deve rejeitar
        assert novo_estado["estado"] == "perguntando_idade"
        assert "18 anos" in resposta.lower()
```

### Salve e rode:

```bash
python rodar_testes.py
```

Pronto! Novo teste adicionado! 🎉

---

## 🐛 TESTES DE REGRESSÃO

**O que é:** Garantir que uma correção não quebrou outra coisa.

**Exemplo real:**

1. Você corrige bug no estado "aguardando_email"
2. Roda os testes
3. **25 passed** ✅ = Nada quebrou!
4. Se aparecer **FAILED** = A correção quebrou algo
5. Arrume antes de fazer deploy

**Por isso os testes são importantes!**

---

## 📊 RELATÓRIOS

### Relatório HTML (`relatorio_testes.html`)

Mostra visualmente:
- ✅ Testes que passaram (verde)
- ❌ Testes que falharam (vermelho)
- 📸 Screenshots de erros
- ⏱️ Tempo de execução

**Como abrir:** Duplo clique no arquivo

### Relatório de Cobertura (`htmlcov/index.html`)

Mostra:
- 📈 % de código testado
- 🔴 Linhas que NÃO têm testes
- 🟢 Linhas que TÊM testes

**Como abrir:** Duplo clique no arquivo

---

## 🎓 GLOSSÁRIO

| Termo | O que significa |
|-------|----------------|
| **Teste Unitário** | Testa UMA função isolada |
| **Teste de Integração** | Testa VÁRIAS funções juntas |
| **Teste E2E** | Testa o fluxo COMPLETO (End-to-End) |
| **Teste de Regressão** | Garante que correções não quebram funcionalidades antigas |
| **Cobertura** | % de código que tem testes |
| **Mock** | Substituir componente real por falso (ex: IA) |
| **Fixture** | Dados de teste reutilizáveis |
| **Assert** | Verificar se algo é verdadeiro |

---

## ❓ PERGUNTAS FREQUENTES

### P: Os testes custam dinheiro?

**R:** Não! Testes rodam localmente e são gratuitos. Apenas pulamos o teste de IA (que usaria API OpenAI) para economizar.

### P: Quanto tempo leva rodar os testes?

**R:** ~5-10 segundos para todos os testes.

### P: Preciso rodar TODA VEZ que mudo algo?

**R:** Idealmente sim, mas no mínimo:
- Antes de fazer commit
- Antes de fazer deploy
- Depois de corrigir bug

### P: E se eu não entender o erro?

**R:** Me manda screenshot do `relatorio_testes.html` que eu te ajudo!

### P: Posso rodar um teste só?

**R:** Sim!
```bash
pytest test_bot_fluxo.py::TestEstadoAguardandoNome::test_nome_valido -v
```

### P: Como testar no Render antes de deploy?

**R:** Os testes rodam localmente. Se passarem aqui, vão passar lá!

---

## 🚀 PRÓXIMOS PASSOS

1. **Rode os testes agora:**
   ```bash
   python rodar_testes.py --html
   ```

2. **Abra o relatório no navegador:**
   - Veja tudo verde ✅
   - Explore os testes
   - Entenda o que cada um faz

3. **Faça uma mudança no código:**
   - Rode os testes novamente
   - Veja se continua tudo verde

4. **Adicione novos testes:**
   - Quando adicionar funcionalidade
   - Quando encontrar bug

---

## 📞 SUPORTE

Se tiver QUALQUER dúvida:
1. Rode os testes
2. Tire screenshot do erro
3. Me manda com a pergunta

**Lembre-se:** Testes são seus amigos! Eles protegem você e seus clientes! 🛡️

---

**Criado por:** Claude Code
**Data:** 16/10/2025
**Versão:** 1.0
