FROM python:3.11
WORKDIR /Verba
COPY . /Verba
RUN pip install '.'
RUN pip install pandas
# Install additional dependencies for resume export functionality
RUN pip install reportlab==4.0.9 python-docx==1.1.2 markdown==3.5.2
# Create exports directory for resume files
RUN mkdir -p /Verba/exports
EXPOSE 8000
CMD ["verba", "start","--port","8000","--host","0.0.0.0"]
