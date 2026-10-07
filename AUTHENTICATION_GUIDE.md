# 🔐 ИНСТРУКЦИЯ ПО АУТЕНТИФИКАЦИИ И ЗАГРУЗКЕ НА GITHUB

## ❗ Проблема
Git не может загрузить проект, так как не настроена аутентификация.
Ошибка: SEC_E_NO_CREDENTIALS - отсутствуют учетные данные.

## ✅ Решение: Создать Personal Access Token (PAT)

GitHub больше не принимает пароли для Git операций.
Вместо этого нужно использовать Personal Access Token.

---

## 📝 ШАГ 1: Создайте Personal Access Token

1. Откройте в браузере: https://github.com/settings/tokens

2. Нажмите кнопку **"Generate new token"** → **"Generate new token (classic)"**

3. Заполните форму:
   - **Note**: ProjectFlow Upload
   - **Expiration**: 90 days (или больше)
   - **Select scopes**: 
     ☑️ **repo** (поставьте галочку - это даст доступ ко всем операциям с репозиторием)

4. Прокрутите вниз и нажмите **"Generate token"**

5. **⚠️ ВАЖНО!** Скопируйте токен (он показывается только ОДИН раз!)
   Токен выглядит примерно так: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

---

## 📝 ШАГ 2: Создайте репозиторий на GitHub (если ещё не создали)

1. Откройте: https://github.com/new

2. Заполните:
   - **Repository name**: ProjectFlow
   - **Description**: Система управления проектами - Производственная практика ПП.02
   - **Public** или **Private** (на ваш выбор)
   - ⚠️ **НЕ ставьте галочки на:**
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license

3. Нажмите **"Create repository"**

---

## 📝 ШАГ 3: Настройте Git Credential Manager (РЕКОМЕНДУЕТСЯ)

Выполните в PowerShell:

```powershell
cd C:\Users\ilnaz_16a9y7w\Documents\deepseek-harness\default-workspace\ProjectFlow-Python

# Настраиваем Git Credential Manager
git config --global credential.helper manager-core

# Проверяем настройку
git config --global credential.helper
```

---

## 📝 ШАГ 4: Загрузите проект на GitHub

Теперь выполните команду push:

```powershell
cd C:\Users\ilnaz_16a9y7w\Documents\deepseek-harness\default-workspace\ProjectFlow-Python

# Загружаем master ветку
git push -u origin master

# Загружаем develop ветку  
git push -u origin develop
```

При первом push **откроется окно аутентификации** или запрос в консоли:

- **Username**: peppapon
- **Password**: вставьте ваш Personal Access Token (ghp_xxx...)

Git Credential Manager сохранит ваши данные, и больше не будет спрашивать.

---

## 🎯 АЛЬТЕРНАТИВНЫЙ СПОСОБ: Использовать SSH ключ

Если хотите использовать SSH вместо HTTPS:

### 1. Проверьте наличие SSH ключа:

```powershell
Test-Path "C:\Users\ilnaz_16a9y7w\.ssh\id_rsa.pub"
```

### 2. Если ключа нет, создайте его:

```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Нажмите Enter 3 раза (используйте значения по умолчанию)
```

### 3. Скопируйте публичный ключ:

```powershell
Get-Content "C:\Users\ilnaz_16a9y7w\.ssh\id_ed25519.pub" | clip
# Ключ скопирован в буфер обмена
```

### 4. Добавьте ключ на GitHub:

- Откройте: https://github.com/settings/ssh/new
- Title: ProjectFlow PC
- Key: вставьте скопированный ключ (Ctrl+V)
- Нажмите "Add SSH key"

### 5. Измените URL репозитория на SSH:

```powershell
cd C:\Users\ilnaz_16a9y7w\Documents\deepseek-harness\default-workspace\ProjectFlow-Python

git remote set-url origin git@github.com:peppapon/ProjectFlow.git

# Теперь можно загрузить без токена
git push -u origin master
git push -u origin develop
```

---

## ✅ После успешной загрузки

Ваш проект будет доступен по адресу:
**https://github.com/peppapon/ProjectFlow**

Проверьте что загрузилось:
- ✓ 37 файлов
- ✓ 12 коммитов  
- ✓ 2 ветки (master, develop)
- ✓ README.md отображается на главной странице
- ✓ Отчёт DOCX в папке docs/

---

## 🆘 Если возникнут проблемы

### Проблема: "Repository not found"
**Решение**: Убедитесь что репозиторий создан на https://github.com/peppapon/ProjectFlow

### Проблема: "Authentication failed"
**Решение**: 
1. Убедитесь что используете Personal Access Token, а не пароль
2. Проверьте что токен имеет права "repo"
3. Попробуйте создать новый токен

### Проблема: "The requested URL returned error: 403"
**Решение**: У токена недостаточно прав. Создайте новый токен с правами "repo"

---

## 📞 Текущий статус проекта

Проект локально готов к загрузке:
- ✅ Git репозиторий настроен
- ✅ Remote добавлен: https://github.com/peppapon/ProjectFlow.git
- ✅ Все файлы закоммичены (37 файлов, 12 коммитов)
- ⏳ Ожидает загрузки на GitHub

---

Создано: 07.10.2026 22:33
