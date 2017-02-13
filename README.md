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

A standard .nlg file starts with a *start phrase* `%`, which is the default entry point for the generator. The generator may also use a specific entry point.

## Phrases

A phrase (`%phrase`) is a general set of token sequences. A phrase is potentially recursive, using tokens which represent other phrases (even itself). Each phrase defines one or more possible sequences.

The regular words in a phrase are ignored in the output tree. This makes them useful for defining higher level grammar for the same intent - for example, for different word orders ("turn on the light" vs "turn the light on").

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

#### Basic generation walkthrough

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

## Values

Sometimes you don't want to ignore the specific words in a sentence, for example to capture the location in a sentence like "how is the weather in boston". Values, marked with a dollar sign as `$value`, are an extension of phrases that also include their regular word tokens in the tree.

```
%getWeather
    what is the weather in $location
    how is the $location weather

$location
    boston
    san francisco
    tokyo
```

```
> what is the weather in san francisco
( %getWeather
    ( $location san francisco ) )
```

## Synonyms

Synonyms, marked `~synonym`, are output only on the sentence side, and are useful for supplying word variations.

```
%good
    ~exclamation this is ~so ~good

~exclamation
    wow
    omg

~so
    so
    very
    extremely

~good
    good
    great
    wonderful
```

```
> wow this is extremely great
( %good )
```

## Optional tokens

Tokens with a `?` at the end will be used only 50% of the time.

```
%findFood
    ~find $price? $food ~near $location
```

```
> find me sushi in san francisco
( %
    ( %findFood
        ( $food sushi )
        ( $location san francisco ) ) )

> tell me the cheap fried chicken around tokyo
( %
    ( %findFood
        ( $price cheap )
        ( $food fried chicken )
        ( $location tokyo ) ) )
```

## Passthrough tokens

Tokens with a `=` at the end are called "passthrough" tokens and will not be included in the output tree, but their children will be. This is defined at the root level, rather than within a token sequence.

```
%
    ~please? %command

%command=
    %getTime
    %getFact

%getTime
    what time is it
    what is the time

%getFact=
    %getLocationFact
    %getPersonFact
    %getPersonalFact
```

In this case, whenever the `%command` token is encountered, whatever its children output will be directly added to the tree (as opposed to prefixed with the `%command` token), so it will be output as `%getTime` or `%getFact`. But in fact `%getFact` is another passthrough token, so the value of its children will be passed all the way up the tree.

```
> what is the time
( %
    ( %getTime ) )

> pretty please what is the population of tokyo
( %
    ( %getLocationFact
        ( $location_fact population )
        ( $location tokyo ) ) )
```

