import './App.css';
import React, { useEffect, useState, useMemo} from 'react';
import axios from 'axios';
import Header from "./component/layout/header";
import Footer from "./component/layout/footer";

const mbti_list = ["INTP", "INTJ", "ENTP", "ENTJ","INFP", "INFJ", "ENFP", "ENFJ", "ISTP",  "ESTP", "ESFP", "ISFP", "ISFJ", "ESTJ",  "ESFJ","ISTJ"]

function App() {
  useEffect(() => {
    setMode("MAIN");
    }, []);

  const [mode, setMode] = useState("");
  const [mbti, setMbti] = useState("");
  const [singer, setSinger] = useState("");
  const [song, setSong] = useState("");
  const [albumArt, setAlbum] = useState("");

  let content = null;

  if (mode === "MAIN") {
    content = <MAIN setMode={setMode} ></MAIN>;
  }
  else if(mode === "SHOW_LIST"){
    content = <ShowMbtiList setMode={setMode} setMbti={setMbti} ></ShowMbtiList>;
  }
  else if(mode === "SEARCH"){
    content = <Search setMode={setMode} setSinger={setSinger} setSong={setSong} setAlbum={setAlbum}></Search>;
  }
  else if(mode === "SCORE"){
    content = <ShowScore setMode={setMode} singer={singer} song={song} albumArt={albumArt}> </ShowScore>;
  }
  else if(mode === "Show_playlist"){
    content = <MbtiTopList setMode={setMode} mbti={mbti}></MbtiTopList>
  }
  

  return (
    <div>
      <div className ='body_container'>
        <div className="App">
          <Header setMode={setMode} />
              {content}
          <Footer />
        </div>
      </div>
    </div>
  );
}
export default App;

function ShowMbtiList(props) {
  const result = [];

  return (
    <div className='second-form'>
      <div className='backBtn' onClick={() => props.setMode("MAIN")}></div>
      <div className='list-wrapper'>
        {mbti_list.map((mbti, index) => (
          <div key={index} className='mbti-wrapper' onClick={() => {
            props.setMbti(mbti);
            props.setMode("Show_playlist");
          }}>
            <img src={`img/${mbti}.png`} alt={mbti} />
            <span>{mbti}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MbtiTopList(props){
  const [ResultList, setSongs] = useState([]); // 검색 결과를 저장할 상태
    useEffect(() => {
      const fetchSongs = async () => {
        try {
          const response = await axios.get(`http://localhost:8000/songs/${props.mbti}`);
          setSongs(response.data);
        } catch (error) {
          console.error("Error fetching songs:", error);
        }
      };
  
      fetchSongs();
    }, [props.mbti]);

    return (
      <div className='third-form'>
        <div className='backBtn' onClick={() => props.setMode("SHOW_LIST")}></div>
        <div className='wrapper'>
          <h2>= {props.mbti}를 위한 추천 곡들 =</h2>
          <img className='mbti_img' src={`img/${props.mbti}.png`} alt={props.mbti} />
        </div>
        
        <div className='search-result'>
          {ResultList.map((item, index) => (
            <div className="songlist" key={index} >
              <img className='AlbumArt'src={item.img_src}></img>
              <div className='songinfo'>
                <p className='songname'>{item.song_title}</p>
                <p className='singer'>{item.artist}</p>
              </div>
              <div className='score'>
                <h3>{Math.round(item.score * 100)}점</h3>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
}


function ShowScore(props){
  const [recommendations, setRecommendations] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect ( () => {
    setIsLoading(true);
    const fetchData = async () => {
    try {
      const response = await axios.post('http://localhost:8000/recommend/', new URLSearchParams({ song_name: props.song, singer: props.singer, img_src: props.albumArt }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      setRecommendations(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error downloading or processing song:', error);
      alert('Server Error : 데이터를 불러오는데 실패했습니다.');
    } 
  };

  fetchData();
  },[]);

  if (isLoading) {
    return (
      <div className='second-form'>
        <img className='loading' src='img/loading.gif'></img>
        <h2> 노래 다운, 분석 중...</h2>
      </div>
    )
  }

  const sortlist = Object.entries(recommendations).sort((a, b) => b[1] - a[1])
  const sortedlist = sortlist.map(([key, value]) => {
    // value 값을 100을 곱하고 정수로 변환
    const updatedValue = Math.round(value * 100);
    return [key, updatedValue];
});

  

  return(
    <div className='third-form'>
      <div className='backBtn2' onClick={() => props.setMode("SEARCH")}></div>
      <div className='result'>
        <div className='wrapper'>
          <img className='mbti_img' src={`img/${sortedlist[0][0]}.png`}></img>
          <h3> {sortedlist[0][0]}</h3>
        </div>
        
        <img className='heart' src='img/heart.png's></img>
        <div className='wrapper'>
          <img className='albumArt' src={props.albumArt}></img>
          <h3>{props.song} - {props.singer}</h3>
        </div>
      </div>
      <div className='bestScore'><h2>BEST 추천 Score : {sortedlist[0][1]}</h2>  </div>
      <div className='remain'>
        <div className='row-container'>
          {sortedlist.slice(1).map((item, index) => (
            <div key={index} className='remain-score'>
              <img className='remain-img' src={`img/${item[0]}.png`}></img>
              <h4>{item[0]} : {item[1]}점</h4>
            </div>
            ))}
        </div>
      </div>

    </div>
  )

}


function Search(props){
  const [searchResult, setSearchResult] = useState([]); // 검색 결과를 저장할 상태
  const [inputValue, setInputValue] = useState(''); // 입력값 상태

  const handleSearch = async () => {
    try {
      const response = await axios.post('http://localhost:8000/spotify_search/', new URLSearchParams({ song_info: inputValue }));
      setSearchResult(response.data); // 검색 결과 상태 업데이트
      //console.log(`검색어: ${inputValue}`); // 콘솔에 입력값 출력
    } catch (error) {
      console.error("검색 요청에 실패했습니다: ", error);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault(); // 페이지 새로고침 방지
    handleSearch(); // 검색 함수 실행
  };

  const handleChange = (event) => {
    setInputValue(event.target.value); // 입력값을 상태로 저장
  };

  return(
    <div className='second-form'>
      <div className='backBtn2' onClick={() => props.setMode("MAIN")}></div>
      <div className='robot-wrapper'>
        <img className="robot2" src='img/robot2.png' />
        <div className="speech-bubble">
          <h3> 삐빅, 노래를 찾아보세요.</h3>
          <h3>MBTI별 궁합 점수를 봐드립니다.</h3>
        </div>
      </div>
      <form class="search" onSubmit={handleFormSubmit}>
        <input type="text" placeholder="노래 제목과 가수를 입력해주세요." value={inputValue} // input의 value를 상태와 연결
        onChange={handleChange}/>
        <img class="searchBtn" src="https://s3.ap-northeast-2.amazonaws.com/cdn.wecode.co.kr/icon/search.png" onClick={handleSearch} />
      </form>
      <div className='search-result'>
        {searchResult.map((item, index) => (
          <div className="songlist" key={index} onClick={() => {
            props.setMode("SCORE");
            props.setSinger(item.singer)
            props.setSong(item.song_name)
            props.setAlbum(item.album_img)   
          }}  >
            <img className='AlbumArt'src={item.album_img}></img>
            <div className='songinfo'>
              <p className='songname'>{item.song_name}</p>
              <p className='singer'>{item.singer}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


function MAIN(props) {

  return(
          <div className='main-form'>
          <div className='main-choice' onClick={() => {
              props.setMode("SEARCH");
            }}>
            <img alt='robot_img' src= "/img/robot.png" />
            <div className='center-text'>음악이랑<br /> MBTI 궁합 보기</div>
          </div>
          <div className='main-choice' onClick={() => {
              props.setMode("SHOW_LIST");
            }}>
            <img alt='robot_img' src= "/img/robot.png" />
            <div className='center-text'>AI 추천<br /> MBTI별 Playlist</div>
          </div>
          </div>
  )

}