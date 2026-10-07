# ИНСТРУКЦИЯ ПО ЗАГРУЗКЕ ПРОЕКТА НА GITHUB

## Шаг 1: Создайте новый репозиторий на GitHub

1. Откройте браузер и перейдите на https://github.com
2. Войдите в свой аккаунт GitHub
3. Нажмите на зеленую кнопку "New" или "+" в правом верхнем углу → "New repository"
4. Заполните форму:
   - Repository name: **ProjectFlow** (или любое другое имя)
   - Description: Система управления проектами - Производственная практика ПП.02
   - Visibility: **Public** (или Private, если хотите)
   - ❌ НЕ ставьте галочки на:
     - Add a README file
     - Add .gitignore
     - Choose a license
   (У нас уже есть все эти файлы!)
5. Нажмите "Create repository"

## Шаг 2: Скопируйте URL вашего репозитория

После создания репозитория GitHub покажет вам страницу с инструкциями.
Скопируйте HTTPS URL вашего репозитория, он будет выглядеть так:

https://github.com/ваш-username/ProjectFlow.git

## Шаг 3: Выполните команды ниже

Откройте PowerShell в директории проекта и выполните:

\\\powershell
cd C:\Users\ilnaz_16a9y7w\Documents\deepseek-harness\default-workspace\ProjectFlow-Python

# Переключаемся на главную ветку
git checkout master

# Сливаем изменения из develop в master
git merge develop

# Добавляем удаленный репозиторий (ЗАМЕНИТЕ URL НА ВАШ!)
git remote add origin https://github.com/ваш-username/ProjectFlow.git

# Загружаем код на GitHub
git push -u origin master

# Также загружаем ветку develop
git checkout develop
git push -u origin develop

# Проверяем что все загружено
git remote -v
\\\

## Шаг 4: Проверьте результат

Обновите страницу вашего репозитория на GitHub.
Вы должны увидеть:
- ✓ Все 37 файлов проекта
- ✓ 12 коммитов
- ✓ 2 ветки (master и develop)
- ✓ README.md будет отображаться на главной странице

## БЫСТРАЯ КОМАНДА (после создания репозитория)

После того как вы создали репозиторий на GitHub и скопировали его URL,
выполните эти команды (ЗАМЕНИТЕ URL!):

\\\powershell
cd C:\Users\ilnaz_16a9y7w\Documents\deepseek-harness\default-workspace\ProjectFlow-Python
git checkout master
git merge develop
git remote add origin https://github.com/ваш-username/ProjectFlow.git
git push -u origin master
git push -u origin develop
\\\

## Если возникнут проблемы

### Проблема: "remote origin already exists"
Решение:
\\\powershell
git remote remove origin
git remote add origin https://github.com/ваш-username/ProjectFlow.git
\\\

### Проблема: Требуется аутентификация
GitHub больше не поддерживает пароли для Git операций.
Вам нужно создать Personal Access Token:

1. Перейдите: https://github.com/settings/tokens
2. Нажмите "Generate new token" → "Generate new token (classic)"
3. Дайте токену имя: "ProjectFlow Upload"
4. Выберите срок действия: 90 days
5. Поставьте галочку на "repo" (это даст все нужные права)
6. Нажмите "Generate token" внизу страницы
7. СКОПИРУЙТЕ токен! (он показывается только один раз)
8. При запросе пароля в Git используйте этот токен вместо пароля

### Проблема: "failed to push some refs"
Если на GitHub уже есть какие-то файлы, выполните:
\\\powershell
git pull origin master --allow-unrelated-histories
git push -u origin master
\\\

## Что будет загружено на GitHub

📦 Всего файлов: 37
📝 Коммитов: 12
📂 Веток: 2 (master, develop)

Структура проекта:
- ✅ Исходный код (src/)
- ✅ Тесты (tests/)
- ✅ Документация (docs/)
- ✅ Конфигурация (config files)
- ✅ CI/CD (GitHub Actions)
- ✅ README.md
- ✅ Итоговый отчёт (DOCX)

## После успешной загрузки

1. Перейдите на https://github.com/ваш-username/ProjectFlow
2. Проверьте что все файлы загружены
3. README.md должен красиво отображаться на главной странице
4. GitHub Actions может автоматически запуститься (если настроены Secrets)
5. Скопируйте ссылку на репозиторий для отчёта

## Ссылка на репозиторий для отчёта

После загрузки ваш репозиторий будет доступен по адресу:
https://github.com/ваш-username/ProjectFlow

Эту ссылку можно указать в отчёте по практике!

---

Создано: 07.10.2026 22:26
