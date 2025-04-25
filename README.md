# code_insights v0.1

## 1 INTRODUÇÃO
No campo da engenharia de software, sistemas de controle de versão tornaram-se essenciais para gerenciar alterações, facilitar a colaboração e manter um histórico do desenvolvimento de projetos. Esses sistemas são fundamentais para acompanhar a evolução do software, permitindo que os desenvolvedores revertam a versões anteriores e compreendam a trajetória das mudanças no código. Contudo, embora o controle de versão seja eficiente na gestão do histórico, a análise da qualidade do código dentro desses sistemas apresenta desafios. Ferramentas existentes muitas vezes carecem da profundidade e da integração necessárias para uma análise completa, especialmente em contextos acadêmicos, onde é importante compreender tendências de qualidade do código ao longo do tempo.
Este estudo aborda a lacuna na integração entre dados de controle de versão e métricas de qualidade de código, propondo uma ferramenta que una esses elementos de forma eficiente para fins de pesquisa acadêmica. A motivação surge da necessidade de uma solução que seja equilibrada, nem demasiado simples nem excessivamente complexa, oferecendo a profundidade necessária para investigações detalhadas. O problema reside na limitação dos métodos atuais, que não conseguem fornecer a integração adequada para análise de tendências de qualidade de código dentro dos sistemas de controle de versão.

## 2 OBJETIVOS
O objetivo principal desta pesquisa é desenvolver uma ferramenta que integre métricas de qualidade de código com dados de controle de versão. Para isso, foram estabelecidos objetivos específicos e mensuráveis:
1. Projetar um sistema de extração de dados: Desenvolver um módulo para extrair dados de repositórios de controle de versão, especialmente do Git, utilizando ferramentas como PyDriller e consultas diretas à API GraphQL (v4) do Github.
2. Implementar métricas de qualidade de código: Incorporar cálculos de diversas métricas de qualidade, incluindo métricas de Halstead (1977) e métricas orientadas a objetos (Chidamber & Kemerer, 1994), potencialmente usando ferramentas como Radon.
3. Desenvolver uma interface interativa: Criar uma interface usando frameworks como Streamlit, para apresentar as métricas de maneira interativa e acessível ao usuário.
4. Exportação de dados e relatórios: Assegurar que a ferramenta possa exportar dados e produzir relatórios em formatos adequados para pesquisa, como PDF e JSON.

## 3 METODOLOGIA
A metodologia adotada para alcançar esses objetivos segue uma abordagem sistemática e rigorosa, alinhada ao método científico. O processo será iterativo, permitindo ajustes contínuos baseados em testes e feedback.
1. Coleta de dados: Utilizar o PyDriller para extrair informações de repositórios Git, capturando histórico de commits, alterações e outros dados relevantes de controle de versão.
2. Cálculo de métricas: Empregar ferramentas de análise estática, como Radon, para calcular métricas de qualidade de código, garantindo a integração entre os dados de controle de versão e as métricas.
3. Desenvolvimento da interface: Criar um painel interativo com Streamlit, possibilitando uma exploração dinâmica e intuitiva dos dados, com gráficos gerados pelo Matplotlib.
4. Geração de relatórios: Formatadores os dados analisados em formatos compatíveis com o meio acadêmico, incluindo gráficos, tabelas e análises detalhadas para utilização em artigos e apresentações.
5. Desenvolvimento, teste e validação: Construir um protótipo, realizar testes com estudos de caso, refinar a ferramenta com base nos resultados e validar seu funcionamento com conjuntos de dados extensos, garantindo robustez e confiabilidade.
Seguindo essa abordagem estruturada, a ferramenta permitirá uma análise aprofundada da evolução do código em relação às métricas de qualidade, atendendo às necessidades específicas da pesquisa acadêmica em engenharia de software. Essa metodologia garante um processo de desenvolvimento rigoroso, contribuindo de forma significativa para o avanço do campo.
