FROM public.ecr.aws/lambda/python:3.11 as build

RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

FROM public.ecr.aws/lambda/python:3.11
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y

COPY --from=build /opt/chrome-linux64/ /opt/chrome
COPY --from=build /opt/chromedriver-linux64/chromedriver /opt/

RUN pip install selenium

RUN mkdir /utils
COPY utils/* utils/

COPY * ./

RUN python3.11 -m pip install -r requirements.txt -t .

# Provides dynamic entry points
CMD ["web_scrape_goodreads.lambda_handler"]