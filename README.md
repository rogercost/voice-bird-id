# Voice Bird ID

*** WORK IN PROGRESS ***

The ultimate goal is to build the back end of an app that will take a user's description of a bird in real time as it is
being observed in the field (via speech-to-text) and be able to identify the bird. The proposed architecture is as 
follows:

1. Find official descriptions of all ABA Area birds and cluster them to come up with a taxonomy.
2. Generate training data using an LLM to output hypothetical birder field recordings of each ABA Area bird.
3. Embed each of these recordings and train a coarse-grained classifier to predict the cluster from #1.
4. Inside each cluster, train a fine-grained classifier to predict the species from the embedding.

## Initialization Steps

1. Download the ABA Checklist from https://www.aba.org/aba-checklist/ (see instructions in `utils.py`).
2. Run `extract_text_descriptions_allaboutbirds.py` to scrape formal descriptions of each bird.
3. Run `collect_description_embeddings` to compute and store embeddings for the descriptions in a pickle file.
4. Run `generate_synthetic_recordings.py` to get 20 LLM-generated synthetic field recording transcripts for each bird.
5. Run `collect_synth_rec_embeddings.py` to compute and store embeddings for all the recording transcripts.
6. Run `train_synthrec_l1_classifier.ipynb` in Google Colab to form the clusters, then train the cluster classifier.

## TODO items

Steps 1-5 above have been run. We now need to update the notebook to do the following:
1. Cluster the description embeddings. Use silhouette score to find optimal # of clusters.
2. Generate a name for each cluster using the birds in it, and an LLM prompt.
3. Train the L1 classifier to predict the cluster.

## DEPRECATED - Version 1, Raw Embedding Similarity Search

v1 is a FastAPI service to match a user-provided bird description with a database of known descriptions, using embedding
similarity search. This project is the back end only and can be used to serve a front end that accepts voice-to-text
for use in the field. To set it up:

1. Create a Python virtual environment and install the dependencies using `pip install -r requirements.txt`.
2. Obtain an ebird API key and store it in an environment variable called `EBIRD_API_KEY`.
3. Run `data_prep/extract_text_descriptions_allaboutbirds.py` to create a directory of text bird descriptions.
4. Start the service using `uvicorn service:app` from the home directory.
5. Navigate to http://localhost:8000/docs in a browser to interact with the service.

This approach will attempt to do a completely raw embedding match, which may lack precision for two reasons: the embedding model likely does not finely differentiate based on different birding-specific terminology, and the formal descriptions of the birds may end up in a completely different embedding neighborhood than rough field descriptions provided by users. To address this, we could contemplate the following update to the design:

1. Use an LLM like DeepSeek or ChatGPT to generate hypothetical field descriptions of each ABA Area bird. Do this via an [API]|(https://github.com/cheahjs/free-llm-api-resources). The prompt may look something like this (tested via DeepSeek 2/28/25, results were decent):
```
You are a birdwatcher who is observing a bird through binoculars. The bird you are observing is a White-Throated Sparrow, but you don't know that, all you know is the visual characteristics of the bird. As you observe the bird, you are speaking into a tape recorder as good a description as you can manage, with the hope of later being able to identify the bird based on this description.

What I would like is 10 different variants of the exact words you might say into the tape recorder, if you were 10 different people, observing under different circumstances with varying visibility, lighting and behavior types. The description can be fairly rough and incomplete, as you may be straining to see the bird and keep it in sight, or it could be a longer and more well-phrased observation of a bird that close up or otherwise easy to see. In your 10 different descriptions, please incorporate a variety of these imagined conditions.

Bear in mind that as a beginning birder you are not going to make a guess at the ID of the bird within the description. The descriptions should include only direct observations - e.g. color, size, shape, markings, behavior etc. and should not speculate as to the actual ID.
```
2. Embed each description, tag it with the species, and train a classifier which we'll call the Family Classifier to predict just the family of the bird, based on the raw embedding vector. Select architecture based on out-of-sample performance, with a preference for small size and fast inference speed that can run on device.
3. For each family, train a second classifier which we'll call the Species Classifier, with the same inputs (raw embeddings) and architecture selection criteria, using only the training data from the birds within that family.

The Species Classifier should not output a single prediction; instead, it should give a likelihood score for each class. This way, we can cross reference its output with the subset of likely birds found for the user's current location and date. (This could be an inline ebird-api call or some form of data "pack" like the ones eBird uses.)

Then, longer term, we can add a voice-to-text layer, and use [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html) to package the app as an Android application.
