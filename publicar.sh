#!/bin/bash
cd "$(dirname "$0")"

echo "=== Publicar Junidigital no GitHub Pages ==="
echo ""

# Inicializar git se não existir
if [ ! -d ".git" ]; then
  echo "📁 A inicializar repositório git..."
  git init
  git remote add origin https://github.com/junicoders/junicoders-platform.git
fi

# Confirmar remote
REMOTE=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE" ]; then
  git remote add origin https://github.com/junicoders/junicoders-platform.git
fi

# Pedir token GitHub
echo "🔑 Cola o teu GitHub Personal Access Token:"
echo "   (cria em: github.com/settings/tokens → Generate new token → classic)"
echo "   Permissões necessárias: repo (full)"
echo ""
read -s -p "Token: " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
  echo "❌ Token vazio. Cancela."
  read -p "Enter para fechar..."
  exit 1
fi

# Commit e push
echo "📦 A preparar ficheiros..."
git add -A
git commit -m "feat: 6 ilhas completas com 87 desafios" 2>/dev/null || git commit --allow-empty -m "update: sincronizar ficheiros"

echo "🚀 A publicar no GitHub..."
git push https://${TOKEN}@github.com/junicoders/junicoders-platform.git main 2>&1

# Se falhou com main, tentar master
if [ $? -ne 0 ]; then
  echo "A tentar branch 'master'..."
  git push https://${TOKEN}@github.com/junicoders/junicoders-platform.git master 2>&1
fi

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Publicado com sucesso!"
  echo "   Aguarda 1-2 minutos e abre:"
  echo "   https://junicoders.github.io/junicoders-platform/"
else
  echo ""
  echo "❌ Erro ao publicar. Verifica se o token tem permissão 'repo'."
fi

echo ""
read -p "Pressiona Enter para fechar..."
