FROM python:3.11
WORKDIR /Verba

# Install Node.js (required for Next.js frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

COPY . /Verba
RUN pip install '.'
RUN pip install pandas
# Install additional dependencies for resume export functionality
RUN pip install reportlab==4.0.9 python-docx==1.1.2 markdown==3.5.2
# Create exports directory for resume files
RUN mkdir -p /Verba/exports
EXPOSE 8000
CMD ["verba", "start","--port","8000","--host","0.0.0.0"]
