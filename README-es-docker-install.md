# Installing Elasticsearch and Kibana using Docker images

**If Elasticsearch is already installed this section may be skipped.**

The following steps are intended to be an abbreviated, summary version of the procedures detailed here:

- Full instructions on how to install **Elasticsearch** using a **Docker** image are available on [Installing Elasticsearch with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).
- Full instructions on how to install **Kibana** using a **Docker** image are available on [Install Kibana with Docker](https://www.elastic.co/guide/en/kibana/8.5/docker.html).

Refer to the above instructions for additional information.

1. Install the **Docker** Desktop application:

   https://docs.docker.com/get-docker/

2. Pull the **Elasticsearch** **Docker** image with the following terminal command:

   `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.5.0`

3. Create a network for **Elasticsearch** with the following command:

   `docker network create elastic`

4. Start **Elasticsearch**:

   `docker run --name es01 --net elastic -p 9200:9200 -p 9300:9300 -it docker.elastic.co/elasticsearch/elasticsearch:8.5.0`

5. The output of the `docker run` command above will include a password for the application and an enrollment token for the **Kibana** application. Save these values for future use.

6. Pull the **Kibana** **Docker** image with the following command:

   `docker pull docker.elastic.co/kibana/kibana:8.5.0`

7. Start **Kibana**:

   `docker run --name kib-01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.5.0`

8. The output of the `docker run` command above will include a link to run **Kibana**. Open that link in a browser and enter the enrollment token saved in step 5 for authentication.

   Note that the enrollment token expires after 30 minutes, so it's best to do this step right away. (Commands to generate new passwords and enrollment tokens are in the full **Kibana** installation instructions listed at the top.)

9. Copy the security certificate to an appropriate location on the local machine:

   `docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .`

   Note the location of this file as it will be used later when running the **Elasticsearch Portal** web application included in this distribution.

7. Test the installation by issuing the following command:

   `curl --cacert http_ca.crt -u elastic https://localhost:9200`

   Enter the password obtained in step 5 when prompted.

**Elasticsearch** and **Kibana** are now ready for use.

[Link back to the Elastic Portal README](README.md)
