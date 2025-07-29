My engine is focused on making the everyday game development process less frustrating and make the simple things easy to do. Not really that focused on the low level details, but on usability. I've basically stopped programming at work now because of how awful it is and rather program using my own framework at home.

Originally Unity stepped in the direction of making games less of a hassle, but they've just been straying further and further from that path in my option.
IMO DOTS is only really useful for a few types of games, but unnecessary for most. I only need a handful of movable/interactable object in my games. Even games that seems complex shouldn't actually be complex underneath.

Also, the iteration time is really bad. In Unity it's over one minute in a big project while in my engine it's close to 0.114 seconds. I really need to be able to work without disruption in order to be productive.

In Unreal, you're supposed to use Blueprint and C++. I don't think I have to say more about that. And the editor is not good either. I get why you say it's for visualizations now, because it's mostly focused on graphics. I would like to have that rendering engine though o_o

As an example, to create a GameObject in Unity at x=1 you write something like this. If I also wanted to add a mesh, god knows how much more code that would be.
```c#
var gameObject = new GameObject("name");
gameObject.transform.localPosition = new Vector3(1.0f, gameObject.transform.localPosition.y, gameObject.transform.localPosition.z);
```

In my engine I write:
```python
entity = Entity(x=1)
```
