# s3 IIIF Utils
s3 Sync and manifest generation program.

To use create the following structure in this project directory:

 * storage
   * gdmrdgital
     * iiif-images
     * iiif-manifests-gdmr
   * .aws-credentials.ini    

where:
 * `gdmrdigital` is the AWS account for s3
 * `iiif-images` matches your bucket name for storing the images you want to serve over IIIF. This bucket can be exposed by using [Cantaloupe docker](https://github.com/glenrobson/cantaloupe-docker/tree/gdmr-deploy)
 * `iiif-manifests-gdmr` is the location to store manifests and any other data you want to share over http using s3 [static web hosting](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html)

The `aws-credentials.ini` contains the following:

```
[credentials]
aws_access_key_id=xxxx
aws_secret_access_key=xxx
region_name=eu-west-2
```

and this gives the `sync.py` script the credentials to access and upload data to your s3 buckets. See the [following](https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) for instructions on creating your public and secret key.

## Scripts

### sync.py

This takes the data in your `storage\aws_account\bucket` and syncs it with s3. It allows you to develop and test locally and then replicate your directory structure on s3. To run do the following:

```
./scripts/sync.py
```

To save transfer costs it tries to only upload files which are new or have been modified.

### dir2manifest.py

This is a program which will generate a manifest from a directory of images. Currently it requires the images are also hosted and available through a IIIF Image server. So if you use this system to host your images then ensure your run `sync.py` before running this program. To run do the following:

```
./scripts/dir2manifest.py storage/gdmrdigtal/iiif-images/owl storage/gdmrdigital/iiif-manifests/owl/owl_manifest.json
```

Where the first parameter is the list of images to add to the manifest and the second parameter is the generated manifest. There are also the following optional parameters:

 * --baseurl-manifest BASEURL_MANIFEST: this is the URL of where the manifest will be accessible over http/https minus the filename.
 * --baseloc-manifest BASELOC_MANIFEST: the root directory on the filesystem for manifests e.g. `storage/gdmrdigital/iiif-manifests-gdmr`
 * --baseurl-image BASEURL_IMAGE: this is the URL of where the iiif-images will be accessible through the IIIF Image server minus the identifier.
 * --baseloc-image BASELOC_IMAGE: this is the root directory for the iiif-images as seen by the IIIF Image server
 * --label LABEL: Optional label to be added to the manifest. This needs to be set either by the metadata file or using this parameter.
 * --description DESCRIPTION: optional description for the manifest
 * --metadatafile METADATAFILE: a way of adding more metadata including label, description, metadata section, license and logo to the manifest. Examples can be seen in the metadata directory of this project.  
 * --image-list IMAGE_LIST: supply this as a text file one file per line if you need a specific order in the manifest.

To keep the command short any of the above parameters can be stored in a config file such as the following:
```
baseurl-manifest=https://iiif.gdmrdigital.com
baseurl-image=https://iiif.gdmrdigital.com/image/iiif/2
baseloc-manifest=storage/gdmrdigital/iiif-manifests-gdmr
baseloc-image=storage/gdmrdigital/iiif-images
```

Examples can be seen in the `config` directory of this project. Keeping it to the above 4 parameters means most of the static data is in a config but the things that chance per manifest can be passed as parameters.

### cacheImages.sh

This goes through all of the images in the `iiif-images` directory and retrieves their info.json. If you are using cantaloupe to server the IIIF Images it means all of the images will be moved from the s3 bucket to be stored locally on the cantaloupe machine.

### downloads3.sh

A script to downdload data from another s3 bucket locally.

### nginx.sh

A script to run docker on this project to test the `iiif-manifests-gdmr` bucket over http.
