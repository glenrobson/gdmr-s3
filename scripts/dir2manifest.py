#!/usr/local/bin/python3

import configargparse
import sys
import os
import json
from os.path import basename
from os.path import dirname
from os import path
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def addSlash(url):
    if url[-1] != '/':
        return url + '/'
    else:
        return url

def getjson(url):
    print ('getting %s' % url)
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

if __name__ == "__main__":

    parser = configargparse.ArgParser(description='Create a manifest from a directory of images.', default_config_files=['config/manifest.config'])
    parser.add('image_dir',nargs=1,  help='Location of the images to use to create the manifest')
    parser.add('manifest_file',nargs=1, help='Location to store the generated manifest.')
    parser.add('--baseurl-manifest',nargs=1, help='Base URL where the manifest will be stored.')
    parser.add('--baseloc-manifest',nargs=1, help='Base file path where manifest will be servered from.')
    parser.add('--baseurl-image',nargs=1, help='Base url where image will be servered from.')
    parser.add('--baseloc-image',nargs=1, help='Base file path where image will be servered from.')
    parser.add('--label',nargs=1, help='Base file path where image will be servered from.')
    parser.add('--description',nargs=1, help='Base file path where image will be servered from.')
    parser.add('--metadatafile',nargs=1, help='JSON file containing metadata fields.')
    parser.add('--image-list',nargs=1, help='JSON file containing metadata fields.')

    options = parser.parse_args()
    imagedir=options.image_dir[0]
    manifest_filename=options.manifest_file[0]
    print (options)
    print ("[imagedir %s, manifest_filename %s]" %(imagedir,manifest_filename))

    image_root = addSlash(options.baseurl_image[0])
    image_prefix = addSlash(imagedir.split(addSlash(options.baseloc_image[0]))[1])
    encodeslash='%2F'

    # Get the last part of the file path as this will be the web accessible part
    print ("mainfest file path: %s (%s)" % (dirname(manifest_filename), manifest_filename))
    prefix=addSlash(dirname(manifest_filename).split(addSlash(options.baseloc_manifest[0]))[1])

    baseurl = addSlash(options.baseurl_manifest[0])
    baseurl += prefix

    manifest = {}
    manifest["@context"] = "http://iiif.io/api/presentation/2/context.json"
    manifest["@id"] = baseurl + basename(manifest_filename)
    manifest["@type"] = "sc:Manifest"


    if options.metadatafile:
        with open(options.metadatafile[0], 'r') as f:
            metadata = json.load(f)
            if 'label' in metadata:
                manifest["label"] = metadata["label"]

            if 'description' in metadata:
                manifest['description'] = metadata['description']

            if 'navDate' in metadata:
                manifest['navDate'] = metadata['navDate']

            if 'metadata' in metadata:
                manifest["metadata"] = metadata["metadata"]
    # Over write label and description if supplied as parameters
    if options.label:
        manifest["label"] = options.label[0]
    if options.description:
        manifest["description"] = options.description[0]
    sequence = {}
    manifest["sequences"] = [ sequence ]
    sequence["@type"] = "sc:Sequence"
    canvases = []
    sequence["canvases"] = canvases
    if options.image_list:
        with open(options.image_list[0], 'r') as imagelist:
            images = []
            for line in imagelist:
                filename = path.join(imagedir,line.strip())
                if path.exists(filename):
                    images.append(line.strip())
                else:
                    print ('File missing %s' % filename)

    else:
        images = os.listdir(imagedir)

    for image in images:
        canvas = {}
        image_id = image[:-4]
        canvases.append(canvas)
        canvas["@id"] = baseurl + "canvas/" + image_id
        canvas["@type"] = "sc:Canvas"
        canvas["label"] = image_id
        imageBaseURI=image_root + image_prefix.replace('/', encodeslash) + image
        imgjson = getjson(imageBaseURI + '/info.json')
        # need to get height and width
        canvas["height"] = imgjson["height"]
        canvas["width"] = imgjson["width"]
        imagejson = {}
        canvas["images"] =  [ imagejson ]
        imagejson["@id"] = "%sanno/image/%s" % (baseurl, image_id)
        imagejson["@type"] = "oa:Annotation"
        imagejson["motivation"] = "sc:painting"
        imagejson["on"] =  canvas["@id"]

        resource = {}
        imagejson ["resource"] = resource
        resource["@id"] = imageBaseURI + '/full/511,/0/default.jpg'
        resource["@type"] = "dctypes:Image"
        resource["format"] = "image/jpeg"
        resource["height"] = imgjson["height"]
        resource["width"] = imgjson["width"]
        resource["service"] = {
            "@context":  "http://iiif.io/api/image/2/context.json",
            "@id": imageBaseURI,
            "profile": "http://iiif.io/api/image/2/level2.json"
        }

    with open(manifest_filename, 'w') as f:
        json.dump(manifest, f, indent=4, sort_keys=False)
