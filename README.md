# nalgene

A natural language generation language, intended for creating training data for intent parsing systems.

## Usage

```
$ python generate.py examples/iot.nlg
> please if the temperature in minnesota is equal to 2 then turn the office light off thanks
( %if
    ( %condition
        ( %currentWeather
            ( $location minnesota ) )
        ( $operator equal to )
        ( $number 2 ) )
    ( %setDeviceState
        ( $device.name office light )
        ( $device.state off ) ) )
```

## Overview

Nalgene generates by reading from a grammar file and outputting pairs of:

* Sentence: the natural language sentence, e.g. "turn on the light"
* Tree: a nested list of tokens ([an s-expression](https://en.wikipedia.org/wiki/S-expression)) generated alongside the sentence, e.g.

	```
    ( %setDeviceState
        ( $device.name light )
        ( $device.state on ) ) )
	```

## Syntax

A .nlg nalgene grammar file is a set of sections separated by a blank line. Every section takes this shape:

```
node_name
    token sequence 1
    token sequence 2
```

The indented lines under a node are the node's possible token sequences. Each token in a sequence is either

* a regular word (no prefix),
* a `%phrase` node,
* a `$value` node,
* or a `~synonym` word.

Each token is added to the output sentence and/or tree during generation, depending on the type.

### Phrases

A phrase (`%phrase`) is a general set of token sequences. A phrase is potentially recursive, using tokens which represent other phrases (even itself). Each phrase defines one or more possible sequences - for example, for different word orders ("turn on the light" vs "turn the light on").

The regular words in a phrase are ignored in the output tree. This makes them useful for defining higher level grammar or intents.

Every .nlg file starts with the *start phrase* `%`, which is the default entry point for the generator.

#### Simple phrases example

Using this grammar: 

```
%
    %greeting
    %farewell
    %greeting and %farewell

%greeting
    hey there
    hi

%farewell
    goodbye
    bye
```

The generator might output:

```
> hey there and bye
( %
    ( %greeting )
    ( %farewell ) )
```

Here's how the generator arrived at this specific sentence and tree pair:

* Start at start node `%`, with an empty output sentence `""` and tree `( % )`
* Randomly choose a token sequence, in this case the 3rd: `%greeting and %farewell`
* The first token is a phrase token `%greeting`, so
    * Add a new sub-tree `( %greeting )` to the parent tree
    * Look up the token sequences for `%greeting`
    * Choose one, in this case `hey there`
        * For both of these regular word tokens, add to the output sentence (but not to the tree)
* At this point the output sentence is `"hey there"` and the parse tree is `( % ( %greeting ) )` 
* The second token is a regular word `"and"`, so add it to the output sentence
* The third token is another phrase `%farewell`, so
    * Add a new sub-tree `( %farewell )` to the parent tree
    * Look up the token sequences for `%farewell`
    * Choose one, in this case `bye`
        * Add to the output sentence
        * Now the output sentence is `"hey there and bye"`
* No more tokens, so we're done

### Values

Sometimes you don't want to ignore the specific words in a sentence, for example to capture the location in a sentence like "how is the weather in boston". Values, marked with a dollar sign as `$value`, are an extension of phrases that also include their regular word tokens in the tree.

```
%
    %getWeather
	%getDistance

%getWeather
    what is the weather in $location
    what is it like in $location
    how is the $location weather

%getDistance
	how far is it to $location
	how far away is $location from here

$location
    boston
    san francisco
    tokyo
```

```
> what is the weather in san francisco
( %
    ( %getWeather
        ( $location san francisco ) ) )
```

### Synonyms

Synonyms, marked `~synonym`, are output only on the sentence side, and are useful for supplying word variations.

```
%
    %happy
    %sad

%happy
    this is ~so ~good

%sad
    this is ~so ~bad

~so
    so
    extremely

~good
    good
    great

~bad
    bad
    terrible
```

```
> this is extremely terrible
( %
    ( %sad ) )
```

