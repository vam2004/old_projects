use std::collections::hash_map::DefaultHasher;
use std::hash::Hasher;
const FILL: u8 = 61;
fn from_64(s: u8) -> Option<u8> {
    if s < 26  {
        return Some(s + 65);
    } else if s < 52 { 
        return Some(s + 71);
    } else if s < 62 {
        return Some(s - 4);
    } else if s < 64 {
        return Some(s * 4 - 205); 
    } else {
        return None;
    }
}
fn to_64(s: u8) -> Option<u8> {
    if s > 47 && s < 58 {
        return Some(s + 4);
    } else if s > 64 && s < 91 {
        return Some(s - 65);
    } else if s > 96 && s < 123 {
        return Some(s - 71);
    } else if s == 43 {
        return Some(62);
    } else if s == 47 {
        return Some(63);
    } else {
        return None;
    }
}
struct BlockEncoder {
    at: u32,
    block: u32
}
enum LiveWork<T>{
    Some(T),
    Feed,
    None
}
impl BlockEncoder {
    fn new() -> Self{
        Self {
            at: 0,
            block: 0
        }
    }
    fn pre_feed(&mut self, s: u32) 
    -> LiveWork<[u8; 4]> {
        let a = self.at;
        let mut b = self.block;
        b |= (s << 16) >> (a << 3);
        return if a == 2 {
            self.at = 0;
            self.block = 0;
            LiveWork::Some(splite_block_v6(b))
        } else {
            self.at += 1;
            self.block = b;
            LiveWork::Feed
        }
    }
    fn feed(&mut self, s: u32) -> LiveWork<[u8; 4]> {
        return match self.pre_feed(s) {
            LiveWork::Some(x) => {
                let mut tmp: [u8; 4] = [0, 0, 0, 0];
                for (i, v) in x.iter().enumerate() {
                    tmp[i] = match from_64(*v) {
                        Some(d) => d,
                        None => return LiveWork::None
                    };
                }
                LiveWork::Some(tmp)
            }
            all => all 
        }
    }
    fn fill(&mut self) -> Option<LiveWork<[u8; 4]>>{
        let a = self.at;
        if a == 0 {
            return None;
        }
        self.at = 2;
        Some(match self.feed(0) {
            LiveWork::Some(mut tmp) => {
                if a == 1 {
                    tmp[2] = FILL;
                }
                tmp[3] = FILL;
                LiveWork::Some(tmp)
            }
            all => all
        })
    }
}
fn splite_block_v6(s: u32) -> [u8; 4] {
    let x0 = ((s >> 18) & 0x3f) as u8;
    let x1 = ((s >> 12) & 0x3f) as u8;
    let x2 = ((s >> 6) & 0x3f) as u8;
    let x3 = (s & 0x3f) as u8;
    [x0, x1, x2, x3]
}
fn splite_block_v8(s: u32) -> [u8; 3] {
    let x0 = (s >> 16) as u8;
    let x1 = (s >> 8) as u8;
    let x2 = s as u8;
    [x0, x1, x2]
}
fn encode(s: Vec<u8>) -> Option<Vec<u8>> {
    let x = s.len();
    let y = (x - (x % 3) + 3) / 3 * 4;
    let mut tmp = Vec::with_capacity(y);
    let mut enc = BlockEncoder::new();
    for v in s.iter() {
        match enc.feed(*v as u32) {
            LiveWork::Some(d) => {
                tmp.append(&mut d.to_vec());
            },
            LiveWork::None => return None,
            _ => {}
        }
    }
    match enc.fill() {
        Some(d0) => match d0 {
            LiveWork::Some(d1) => tmp
                .append(&mut d1.to_vec()),
            _ => return None
        },
        None => {}
    }
    Some(tmp)
}
fn print_bytes(s: &[u8]) {
    println!("{}", fmt_bits(s, 8, " "));
}
fn fmt_bits(s: &[u8], a: usize, d: &str) -> String{
    let l = s.len() * (a + d.len());
    let mut y = String::with_capacity(l);
    for x in s.iter(){
        y.push_str(&mut format!("{:0>a$b}{d}", x));
    };
    y
}
fn remove_indent(s: String) -> String {
    s.replace("\n", " ").replace("\t", "")
}
fn make_test() -> (String, String) {
    let s0 = r#"Man is distinguished, not
only by his reason, but by this singular
passion from other animals, which is a
lust of the mind, that by a perseverance
of delight in the continued and
indefatigable generation of knowledge,
exceeds the short vehemence of any carnal
pleasure."#;
    let s1 = "TWFuIGlzIGRpc3Rpbmd1aXNoZWQs\
IG5vdCBvbmx5IGJ5IGhpcyByZWFzb24sIGJ1dCB\
ieSB0aGlzIHNpbmd1bGFyIHBhc3Npb24gZnJvbS\
BvdGhlciBhbmltYWxzLCB3aGljaCBpcyBhIGx1c\
3Qgb2YgdGhlIG1pbmQsIHRoYXQgYnkgYSBwZXJz\
ZXZlcmFuY2Ugb2YgZGVsaWdodCBpbiB0aGUgY29\
udGludWVkIGFuZCBpbmRlZmF0aWdhYmxlIGdlbm\
VyYXRpb24gb2Yga25vd2xlZGdlLCBleGNlZWRzI\
HRoZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNh\
cm5hbCBwbGVhc3VyZS4=";
    let r0 = remove_indent(String::from(s0));
    let r1 = remove_indent(String::from(s1)
        .replace(" ", ""));
    (r0, r1)
}
enum ResAndOpt<T> {
    Some(T),
    None,
    Err
}
struct BlockDecoder {
    at: u32,
    block: u32
}
impl BlockDecoder {
    fn new () -> Self{
        Self{
            at: 0,
            block: 0
        }
    }
    fn pre_feed (&mut self, s: u32) 
        -> LiveWork<[u8; 3]>  {
        let a = self.at;
        let mut b = self.block;
        b |= (s & 0x3f) << (18 - (a * 6));
        return if a == 3 {
            self.at = 0;
            self.block = 0;
            LiveWork::Some(splite_block_v8(b))
        } else {
            self.at += 1;
            self.block = b;
            LiveWork::Feed
        }
    }
    fn feed(&mut self, s: u8) -> LiveWork<[u8; 3]> {
        let tmp: u32 = match to_64(s) {
            Some(x) => x as u32,
            None => return LiveWork::None
        };
        self.pre_feed(tmp)
    }
    fn end (&mut self) -> ResAndOpt<Vec<u8>> {
        let a = self.at;
        if a == 0 {
            return ResAndOpt::None;
        }
        if a == 1 {
            return ResAndOpt::Err;
        }
        self.at = 3;
        let tmp = match self.pre_feed(0) {
            LiveWork::Some(data) => data,
            _ => return ResAndOpt::Err
        };
        let mut res = vec![tmp[0]];
        if a == 3 {
            res.push(tmp[1]);
        }
        ResAndOpt::Some(res)
    }
}
fn decode(s: Vec<u8>) -> Option<Vec<u8>>{
    let x = s.len();
    if x % 4 != 0 {
        return None;
    }
    let y = x / 4 * 3;
    let mut tmp: Vec<u8> = Vec::with_capacity(y);
    let mut enc = BlockDecoder::new();
    for x in s.iter() {
        if *x == FILL {
            break;
        }
        match enc.feed(*x) {
            LiveWork::Some(d) => {
                tmp.append(&mut d.to_vec());
            }
            LiveWork::None => {
                println!("None: {}", *x);
                return None;
            },
            LiveWork::Feed => {}
        }
    }
    match enc.end() {
        ResAndOpt::Some(d) => {
            tmp.append(&mut d.to_vec());
        }
        ResAndOpt::Err => return None,
        ResAndOpt::None => {}
    }
    Some(tmp)
}
fn main () {
    //test_1();
    //test_2();
    //test_3();
    //test_4();
    //test_5();
    println!("{}", test_against("jklmt"));
}
#[test]
fn test_1(){
    let (s0, s1) = make_test();
    let res = encode(s0.as_bytes()
        .to_vec()).unwrap();
    let conv = std::str::from_utf8(
        &res[..]).unwrap();
    assert!(s1 == conv, "{}", 
        format!("{}\n{}", s1, conv));
}
#[test]
fn test_2 () {
    let x: Vec<u8> = "TWF".as_bytes().to_vec();
    let mut enc = BlockDecoder::new();
    for v in x.iter() {
        enc.feed(*v);
    }
    let d = match enc.feed(b'u') {
        LiveWork::Some(d) => d,
        _ => panic!("Get 'None' or 'Feed'")
    };
    let y = [77, 97, 110];
    assert!(y == d, "got:{:?}\nbut:{:?}", y, d);
}
#[test]
fn test_3 () {
    let (s0, s1) = make_test();
    let mut x = decode(s1.as_bytes().to_vec())
        .unwrap();
    let y = std::str::from_utf8(&mut x)
        .unwrap();
    assert!(y == s0, "{}", format!("got:{y}\nbut{s0}"));
}
#[test]
fn test_4 () {
    let x = "ZS4=";
    let mut y = decode(x.as_bytes().to_vec())
        .unwrap();
    let z = std::str::from_utf8(&mut y)
        .unwrap();
    assert!(z == "e.");
}
fn test_against(by: &str) -> String {
    let tmp = encode(by.as_bytes().to_vec()).unwrap();
    let mut res = tmp.clone();
    let mut dec = decode(tmp).unwrap();
    let out = std::str::from_utf8(&mut dec).unwrap();
    assert!(by == out, "{}", format!("got:{out}\nbut:{by}"));
    std::str::from_utf8(&mut res).unwrap().to_string()
}

fn hash_string(s: &str) -> Vec<u8> {
    let mut work = DefaultHasher::new();
    work.write(s.as_bytes());
    let x: u64 = work.finish();
    (0..8).map(|z| cut8_64(x, z)).collect()
}
fn cut8_64(s: u64, a: u64) -> u8 {
    (s >> (56 - 8 * (a & 0x7))) as u8
}