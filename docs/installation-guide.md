# Guia de Instalação e Uso - Code Insights

## 📋 Requisitos do Sistema

### Requisitos Mínimos
- **Python**: 3.8 ou superior
- **Sistema Operacional**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Memória RAM**: 4GB mínimo, 8GB recomendado
- **Espaço em Disco**: 2GB livres (mais espaço para repositórios clonados)
- **Internet**: Conexão ativa para API GitHub e clonagem de repositórios

### Dependências de Sistema
- **Git**: Versão 2.20 ou superior
- **Python pip**: Para instalação de pacotes

## 🚀 Instalação

### Método 1: Instalação Padrão

#### 1. Clone o Repositório
```bash
git clone https://github.com/your-org/code_insights.git
cd code_insights
```

#### 2. Crie um Ambiente Virtual (Recomendado)
```bash
# Python venv
python -m venv venv

# Ativar no Windows
venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

#### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

#### 4. Configure as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
API_KEY=your_github_personal_access_token
GITHUB_API_URL=https://api.github.com/graphql
CLONE_REPOS_BASE=/absolute/path/to/clone/directory
```

### Método 2: Instalação com Conda

```bash
# Criar ambiente conda
conda create -n code_insights python=3.9
conda activate code_insights

# Instalar dependências principais via conda
conda install pandas numpy matplotlib

# Instalar dependências específicas via pip
pip install streamlit radon pydriller python-decouple requests
```

### Método 3: Instalação via Docker (Futuro)

```dockerfile
# Dockerfile (exemplo para desenvolvimento futuro)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["streamlit", "run", "visualization.py"]
```

## 🔧 Configuração

### 1. Token do GitHub

#### Obtenção do Token
1. Acesse [GitHub → Settings → Developer settings](https://github.com/settings/tokens)
2. Clique em "Personal access tokens" → "Tokens (classic)"
3. Clique em "Generate new token"
4. Selecione as permissões:
   - ✅ `repo` (acesso completo a repositórios)
   - ✅ `public_repo` (acesso a repositórios públicos)
   - ✅ `read:org` (leitura de organizações)

#### Configuração do Token
```bash
# Método 1: Arquivo .env
echo "API_KEY=ghp_your_token_here" >> .env

# Método 2: Variável de ambiente
export API_KEY=ghp_your_token_here

# Método 3: Windows CMD
set API_KEY=ghp_your_token_here
```

### 2. Diretório de Clones

#### Configuração do Diretório Base
```bash
# Criar diretório para repositórios
mkdir -p /path/to/clones
chmod 755 /path/to/clones

# Configurar no .env
echo "CLONE_REPOS_BASE=/path/to/clones" >> .env
```

#### Estrutura Resultante
```
/path/to/clones/
├── django/
│   └── django/          # Repositório clonado
├── scikit-learn/
│   └── scikit-learn/    # Repositório clonado
└── ...
```

### 3. Configuração de Repositórios

Edite o arquivo `data.py` para definir repositórios de interesse:
```python
repos = {
    'django': 'django',
    'scikit-learn': 'scikit-learn',
    'microsoft': 'vscode',
    'facebook': 'react',
    'google': 'tensorflow'
}
```

## 🎯 Primeiros Passos

### 1. Teste da Instalação

#### Verificar Dependências
```bash
python -c "
import streamlit
import pandas
import radon
import pydriller
print('✅ Todas as dependências instaladas com sucesso!')
"
```

#### Teste do Token GitHub
```bash
python -c "
from decouple import config
import requests

token = config('API_KEY')
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.github.com/user', headers=headers)
print(f'Token status: {response.status_code}')
if response.status_code == 200:
    print('✅ Token GitHub configurado corretamente!')
else:
    print('❌ Erro na configuração do token')
"
```

### 2. Primeira Análise

#### Análise Simples via CLI
```bash
python main.py
```

**Saída esperada**:
```
Analisando projeto: django
Métricas Chidamber & Kemerer:
{arquivo: {classe: {WMC: X, DIT: Y, ...}}}

Estatísticas do Projeto:
{total_loc: XXXX, mean_complexity: X.XX, ...}
```

#### Interface Web
```bash
streamlit run visualization.py
```

Acesse: http://localhost:8501

### 3. Configuração Personalizada

#### Clonar Repositório Específico
```python
import utils

# Clonar repositório customizado
repos = {"your-org": "your-repo"}
success = utils.clone_repo(repos)

if success:
    print("Repositório clonado com sucesso!")
```

#### Análise Personalizada
```python
import analytics

# Analisar projeto local
project_path = "/path/to/your/project"
metrics = analytics.get_project_metrics(project_path)
ck_metrics = analytics.get_ck_metrics(project_path)

print(f"Arquivos analisados: {len(metrics)}")
```

## 📊 Usando a Interface Streamlit

### 1. Configuração de Repositório

1. **Sidebar → "1. Obtenção do Repositório"**
   - Digite o autor/organização
   - Digite o nome do repositório
   - Clique em "Obter repositório!"

2. **Aguarde o clone**
   - O sistema fará download do repositório
   - Progresso será exibido no console

### 2. Seleção e Análise

1. **"2. Seleção do Repositório"**
   - Escolha um repositório na lista dropdown
   - Selecione a branch (main/master)
   - Marque as métricas desejadas:
     - ✅ Métricas de Halstead e Raw
     - ✅ Métricas de Chidamber & Kemerer  
     - ✅ Issues via GitHub API v4

2. **Configuração Temporal**
   - Selecione Marco Temporal 1 (data início)
   - Selecione Marco Temporal 2 (data fim)
   - Ajuste o tamanho da janela (em meses)

3. **Executar Análise**
   - Clique em "Analisar!"
   - Aguarde o processamento

### 3. Interpretação dos Resultados

#### Seção 1: Issues do Projeto
- Total de issues abertas
- Duração do projeto
- Taxa de criação de issues
- Intervalos entre issues

#### Seção 2: Métricas por Arquivo
- LOC, LLOC, SLOC por arquivo
- Complexidade ciclomática
- Índice de manutenibilidade

#### Seção 3: Estatísticas Gerais
- Totais agregados do projeto
- Médias de complexidade e manutenibilidade
- Número de arquivos processados

#### Seção 4: Métricas C&K
- WMC, DIT, NOC, RFC, CBO, LCOM por classe
- Organizadas por arquivo e classe

## 🛠️ Solução de Problemas

### Problemas Comuns

#### 1. Erro: "ModuleNotFoundError: No module named 'pydriller'"
```bash
# Solução: Reinstalar dependências
pip install --upgrade -r requirements.txt

# Ou instalar individualmente
pip install pydriller
```

#### 2. Erro: "API rate limit exceeded"
```bash
# Verificar limite da API
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit

# Aguardar reset ou usar token com mais privilégios
```

#### 3. Erro: "Permission denied: git command"
```bash
# Verificar instalação do Git
git --version

# Reinstalar Git se necessário
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt-get install git
```

#### 4. Erro: "FileNotFoundError: [Errno 2] No such file"
```bash
# Verificar configuração do diretório base
ls -la $CLONE_REPOS_BASE

# Criar diretório se não existir
mkdir -p $CLONE_REPOS_BASE
```

### Logs e Debug

#### Ativar Modo Debug
```python
# Adicionar no início do script
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Logs do Streamlit
```bash
# Executar com logs detalhados
streamlit run visualization.py --logger.level=debug
```

### Performance

#### Otimizações Recomendadas

1. **Usar SSD**: Para melhor performance de I/O
2. **Limitar Repositórios**: Analisar poucos repos por vez
3. **Cache de Clones**: Reutilizar repositórios já clonados
4. **Filtrar Arquivos**: Excluir arquivos de teste se necessário

```python
# Exemplo de filtro personalizado
def should_analyze_file(filepath):
    # Ignorar arquivos de teste
    if '/test' in filepath or 'test_' in filepath:
        return False
    # Ignorar arquivos muito grandes
    if os.path.getsize(filepath) > 1024 * 1024:  # 1MB
        return False
    return True
```

## 📚 Recursos Adicionais

### Documentação
- [API Reference](api-reference.md)
- [Arquitetura do Sistema](architecture.md)
- [Fluxo do Pipeline](pipeline-flow.md)
- [Diagrama de Classes](class-diagram.md)

### Exemplos
```python
# Ver exemplos completos em:
examples/
├── basic_analysis.py
├── temporal_analysis.py
├── custom_metrics.py
└── batch_processing.py
```

### Suporte
- **Issues**: Reporte bugs no GitHub
- **Documentação**: Consulte os arquivos em `docs/`
- **API**: Veja referência completa da API

### Contribuição
```bash
# Fork do projeto
git clone https://github.com/your-username/code_insights.git

# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Fazer alterações e commit
git commit -am "Adiciona nova funcionalidade"

# Push e Pull Request
git push origin feature/nova-funcionalidade
```