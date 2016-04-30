#!/usr/bin/env python

import simplejson
import pandas as pd
from firebase import firebase

FIREBASE_URL = 'https://ascension.firebaseio.com'
db = firebase.FirebaseApplication(FIREBASE_URL, None)

def collectVpes()

	firebase = firebase.FirebaseApplication(FIREBASE_URL, None)
	base = firebase.get('/', None)


var ref = new Firebase("https://dinosaur-facts.firebaseio.com/dinosaurs");
ref.orderByChild("height").on("child_added", function(snapshot) {
  console.log(snapshot.key() + " was " + snapshot.val().height + " meters tall");
});