# Requirements Wizard - reqwizard

A smart installer for Python requirements files.  
Checks installed packages and versions, installs or updates as needed.

Um instalador inteligente para arquivos de requirements Python.  
Verifica pacotes instalados e versões, instala ou atualiza conforme necessário.

## Compatibility / Compatibilidade

Requires `Python 3.10` or higher  
Requer `Python 3.10` ou superior

## How to install / Como Instalar
<br>
Install reqwizard via pip from PyPI:  
Instale o reqwizard via pip a partir do PyPI:

```bash
pip install reqwizard
```
<br>

## Usage / Uso
<br>
Run reqwizard in your project folder to install or update dependencies from the default `requirements.txt` file:  
Execute o reqwizard na pasta do seu projeto para instalar ou atualizar dependências a partir do arquivo padrão `requirements.txt`:

```bash
reqwizard
```  
<br>
To specify a custom requirements file, use the --file (or -f) option:  
Para especificar um arquivo de requirements personalizado, use a opção --file (ou -f):

```bash
preqwizard --file custom_requirements.txt
```
<br>
To perform a dry run (only check and show what would be installed or updated, without changing anything), use:  
Para fazer uma simulação (dry run), que apenas verifica e mostra o que seria instalado ou atualizado, sem alterar nada, use:

```bash
reqwizard --dry-run
```
<br>
To check the installed version of reqwizard, use:  
Para checar a versão instalada do reqwizard, use:

```bash
reqwizard --version
```


## License / Licença

This project is licensed under the MIT License. See the [LICENSE](https://github.com/mreddwolf/reqwizard/blob/main/LICENSE) file for details.  
Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENÇA](https://github.com/mreddwolf/reqwizard/blob/main/LICENSE) para detalhes.