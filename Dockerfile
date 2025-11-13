FROM python:3.11
WORKDIR /Verba

# Install Node.js (required for Next.js frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

COPY . /Verba

# Build Next.js frontend FIRST (before pip install so it's included in the package)
WORKDIR /Verba/frontend

# Create the target directory for build output
RUN mkdir -p /Verba/goldenverba/server/frontend/out

# Install dependencies and build
RUN npm install
RUN npm run build

# Verify the build contains new tabs
RUN echo "Verifying build..." && \
    ls -la /Verba/goldenverba/server/frontend/out/ && \
    grep -q "WORKLOGS" /Verba/goldenverba/server/frontend/out/_next/static/chunks/app/*.js && \
    echo "✓ New tabs found in build!" || echo "✗ WARNING: New tabs NOT found in build!"

# Return to main directory
WORKDIR /Verba

# NOW install Python package (with built frontend included via MANIFEST.in)
RUN pip install '.'
RUN pip install pandas
# Install additional dependencies for resume export functionality
RUN pip install reportlab==4.0.9 python-docx==1.1.2 markdown==3.5.2

# Create exports directory for resume files
RUN mkdir -p /Verba/exports

EXPOSE 8000
CMD ["verba", "start","--port","8000","--host","0.0.0.0"]
